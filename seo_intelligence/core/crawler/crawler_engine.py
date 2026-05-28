"""
core/crawler/crawler_engine.py
────────────────────────────────
Main crawl orchestrator.
  1. Discover URLs via sitemap (with robots.txt fallback)
  2. Fallback: crawl from homepage if no sitemap found
  3. Fetch all pages async in batches
  4. Persist results to DB
  5. Report progress via a callback (for Streamlit progress bars)
"""

from __future__ import annotations

import asyncio
from typing import Callable, List, Optional

from config.settings import CRAWLER
from core.crawler.sitemap_parser import discover_and_parse_sitemap
from core.crawler.page_fetcher  import AsyncPageFetcher, PageData, fetch_pages_sync
from database import db
from utils.helpers import get_domain, normalise_url
from utils.logger import get_logger

log = get_logger(__name__)

BATCH_SIZE = 50   # pages fetched per async batch


class CrawlerEngine:
    """
    High-level crawler.

    Parameters
    ----------
    base_url        : The site root, e.g. "https://example.com"
    language_filter : "ar" | "en" | "auto"
    max_pages       : Override CRAWLER["max_pages"]
    progress_cb     : Optional callback(current, total) for UI progress
    """

    def __init__(
        self,
        base_url: str,
        language_filter: str = "auto",
        max_pages: Optional[int] = None,
        progress_cb: Optional[Callable[[int, int], None]] = None,
    ):
        self.base_url        = base_url.rstrip("/")
        self.base_domain     = get_domain(base_url)
        self.language_filter = language_filter
        self.max_pages       = max_pages or CRAWLER.get("max_pages") or 50_000
        self.progress_cb     = progress_cb or (lambda c, t: None)

        self._session_id: Optional[int] = None
        self._fetcher = AsyncPageFetcher(self.base_domain, language_filter)

    # ─── Public API ───────────────────────────────────────────────────────────

    def run(self) -> int:
        """
        Full crawl pipeline (blocking).
        Returns the DB session_id for downstream analysis.
        """
        log.info("Starting crawl: %s", self.base_url)

        # 1. Create DB session
        self._session_id = db.create_crawl_session(self.base_domain,
                                                    self.language_filter)

        # 2. Discover URLs
        urls = self._discover_urls()
        if not urls:
            log.warning("No URLs discovered for %s", self.base_url)
            db.finish_crawl_session(self._session_id, 0, "No URLs discovered")
            return self._session_id

        # Apply language filter & page cap
        urls = urls[:self.max_pages]
        log.info("Crawling %d pages", len(urls))

        # 3. Fetch in batches
        all_pages = self._fetch_in_batches(urls)

        # 4. Persist
        self._persist(all_pages)

        # 5. Finish
        db.finish_crawl_session(self._session_id, len(all_pages))
        log.info("Crawl complete: %d pages stored (session %d)",
                 len(all_pages), self._session_id)
        return self._session_id

    # ─── Discovery ────────────────────────────────────────────────────────────

    def _discover_urls(self) -> List[str]:
        urls = discover_and_parse_sitemap(self.base_url)
        if not urls:
            log.info("No sitemap found — falling back to link crawl")
            urls = self._fallback_crawl()
        return urls

    def _fallback_crawl(self) -> List[str]:
        """
        Simple BFS link crawl from the homepage when no sitemap exists.
        Only follows internal links up to max_pages.
        """
        seen:    set[str] = set()
        queue:   list[str] = [self.base_url]
        found:   list[str] = []

        while queue and len(found) < self.max_pages:
            batch  = queue[:BATCH_SIZE]
            queue  = queue[BATCH_SIZE:]
            pages  = fetch_pages_sync(batch, self.base_domain, self.language_filter)

            for page in pages:
                if page.error or page.url in seen:
                    continue
                seen.add(page.url)
                found.append(page.url)

                for link in page.internal_links:
                    target = link["target_url"]
                    if target not in seen and target not in queue:
                        queue.append(target)

        log.info("Fallback crawl found %d pages", len(found))
        return found

    # ─── Batched async fetching ───────────────────────────────────────────────

    def _fetch_in_batches(self, urls: List[str]) -> List[PageData]:
        total   = len(urls)
        results: list[PageData] = []

        for start in range(0, total, BATCH_SIZE):
            batch  = urls[start : start + BATCH_SIZE]
            pages  = fetch_pages_sync(batch, self.base_domain, self.language_filter)
            results.extend(pages)

            done = min(start + BATCH_SIZE, total)
            self.progress_cb(done, total)
            log.debug("Fetched %d / %d", done, total)

        return results

    # ─── Persistence ──────────────────────────────────────────────────────────

    def _persist(self, pages: List[PageData]):
        pages_data = []
        links_data = []

        for p in pages:
            if p.error:
                continue

            pages_data.append({
                "session_id":       self._session_id,
                "url":              p.url,
                "status_code":      p.status_code,
                "title":            p.title,
                "meta_description": p.meta_description,
                "canonical":        p.canonical,
                "h1":               p.h1,
                "word_count":       p.word_count,
                "language":         p.language,
                "body_text":        p.body_text,
            })

        # Bulk insert pages first
        if pages_data:
            page_ids = db.bulk_insert_pages(pages_data)

            # Map URL → page_id
            url_to_id = {
                pd["url"]: pid
                for pd, pid in zip(pages_data, page_ids)
            }

            for p in pages:
                if p.error:
                    continue
                src_id = url_to_id.get(p.url)
                if not src_id:
                    continue
                for link in p.internal_links:
                    links_data.append({
                        "session_id":     self._session_id,
                        "source_page_id": src_id,
                        "target_url":     link["target_url"],
                        "anchor_text":    link["anchor_text"],
                        "link_position":  link["link_position"],
                    })

            if links_data:
                db.bulk_insert_links(links_data)
                log.info("Stored %d pages and %d internal links",
                         len(pages_data), len(links_data))
