"""
core/crawler/page_fetcher.py
─────────────────────────────
Async page fetcher.
  • Concurrent via asyncio + aiohttp
  • Retry system with exponential back-off (tenacity)
  • Per-domain rate limiting
  • User-Agent rotation
  • Extracts: URL, status, title, meta_description, canonical, H1,
              word_count, language, body_text, all_internal_links
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException

from config.settings import CRAWLER
from utils.helpers import (
    build_headers, clean_text, count_words,
    get_domain, is_internal_url, resolve_url,
)
from utils.logger import get_logger

log = get_logger(__name__)


# ─── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class PageData:
    url:              str
    status_code:      int             = 0
    title:            Optional[str]   = None
    meta_description: Optional[str]   = None
    canonical:        Optional[str]   = None
    h1:               Optional[str]   = None
    word_count:       int             = 0
    language:         Optional[str]   = None
    body_text:        str             = ""
    internal_links:   List[dict]      = field(default_factory=list)
    error:            Optional[str]   = None


# ─── Rate limiter (per domain) ────────────────────────────────────────────────

class DomainRateLimiter:
    def __init__(self, delay: float):
        self._delay = delay
        self._last: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def wait(self, domain: str):
        async with self._lock:
            last = self._last.get(domain, 0.0)
            wait = self._delay - (time.monotonic() - last)
            if wait > 0:
                await asyncio.sleep(wait)
            self._last[domain] = time.monotonic()


# ─── Core fetcher ─────────────────────────────────────────────────────────────

class AsyncPageFetcher:
    """
    Fetch a batch of URLs concurrently.

    Usage:
        fetcher = AsyncPageFetcher(base_domain="example.com")
        results = await fetcher.fetch_all(urls)
    """

    def __init__(self, base_domain: str, language_filter: str = "auto"):
        self.base_domain     = base_domain
        self.language_filter = language_filter
        self._semaphore      = asyncio.Semaphore(CRAWLER["max_concurrent_requests"])
        self._rate_limiter   = DomainRateLimiter(CRAWLER["rate_limit_delay"])

    async def fetch_all(self, urls: List[str]) -> List[PageData]:
        """Fetch all URLs concurrently, return list of PageData."""
        connector = aiohttp.TCPConnector(
            limit=CRAWLER["max_concurrent_requests"] * 2,
            ssl=False,
        )
        timeout = aiohttp.ClientTimeout(total=CRAWLER["request_timeout"])

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = [self._fetch_one(session, url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        pages: list[PageData] = []
        for r in results:
            if isinstance(r, Exception):
                log.warning("Unexpected error: %s", r)
            elif isinstance(r, PageData):
                pages.append(r)
        return pages

    async def _fetch_one(self, session: aiohttp.ClientSession, url: str) -> PageData:
        domain = get_domain(url)
        async with self._semaphore:
            await self._rate_limiter.wait(domain)

            for attempt in range(1, CRAWLER["retry_attempts"] + 1):
                try:
                    async with session.get(
                        url,
                        headers=build_headers(),
                        allow_redirects=CRAWLER["follow_redirects"],
                        max_redirects=5,
                    ) as resp:
                        status = resp.status
                        if status != 200:
                            return PageData(url=url, status_code=status,
                                            error=f"HTTP {status}")
                        html = await resp.text(encoding="utf-8", errors="replace")
                        return self._parse_html(url, status, html)

                except asyncio.TimeoutError:
                    log.debug("Timeout on %s (attempt %d)", url, attempt)
                except aiohttp.ClientError as exc:
                    log.debug("Client error on %s: %s (attempt %d)", url, exc, attempt)
                except Exception as exc:
                    log.warning("Error fetching %s: %s", url, exc)
                    break

                if attempt < CRAWLER["retry_attempts"]:
                    await asyncio.sleep(CRAWLER["retry_delay"] * attempt)

            return PageData(url=url, error="max_retries_exceeded")

    # ─── HTML parsing ─────────────────────────────────────────────────────────

    def _parse_html(self, url: str, status: int, html: str) -> PageData:
        soup = BeautifulSoup(html, "lxml")

        # ── Title ─────────────────────────────────────────────────────────────
        title_tag = soup.find("title")
        title = clean_text(title_tag.get_text()) if title_tag else None

        # ── Meta Description ──────────────────────────────────────────────────
        meta_desc = None
        for attr in [{"name": "description"}, {"property": "og:description"}]:
            tag = soup.find("meta", attrs=attr)
            if tag and tag.get("content"):
                meta_desc = clean_text(tag["content"])
                break

        # ── Canonical ─────────────────────────────────────────────────────────
        canonical = None
        can_tag = soup.find("link", rel="canonical")
        if can_tag and can_tag.get("href"):
            canonical = can_tag["href"].strip()

        # ── H1 ────────────────────────────────────────────────────────────────
        h1_tag = soup.find("h1")
        h1 = clean_text(h1_tag.get_text()) if h1_tag else None

        # ── Body text & word count ────────────────────────────────────────────
        # Remove nav, header, footer, scripts, styles
        for tag in soup(["script", "style", "nav", "header", "footer",
                          "aside", "noscript"]):
            tag.decompose()

        main = soup.find("main") or soup.find("article") or soup.find("body")
        raw_text = clean_text(main.get_text(separator=" ")) if main else ""
        word_count = count_words(raw_text)

        # ── Language detection ────────────────────────────────────────────────
        language = self._detect_language(raw_text)

        # ── Internal links ────────────────────────────────────────────────────
        internal_links = self._extract_internal_links(soup, url)

        return PageData(
            url=url,
            status_code=status,
            title=title,
            meta_description=meta_desc,
            canonical=canonical,
            h1=h1,
            word_count=word_count,
            language=language,
            body_text=raw_text[:50_000],   # cap stored text at 50 k chars
            internal_links=internal_links,
        )

    def _detect_language(self, text: str) -> Optional[str]:
        try:
            if len(text) > 50:
                return detect(text[:2000])
        except LangDetectException:
            pass
        return None

    def _extract_internal_links(self, soup: BeautifulSoup, page_url: str) -> List[dict]:
        links = []
        for idx, a_tag in enumerate(soup.find_all("a", href=True)):
            href   = a_tag["href"].strip()
            target = resolve_url(href, page_url)
            if not target:
                continue
            if not is_internal_url(target, self.base_domain):
                continue

            anchor = clean_text(a_tag.get_text())
            links.append({
                "target_url":    target,
                "anchor_text":   anchor or "",
                "link_position": idx,
            })
        return links


# ─── Sync convenience wrapper ─────────────────────────────────────────────────

def fetch_pages_sync(urls: List[str], base_domain: str,
                     language_filter: str = "auto") -> List[PageData]:
    """
    Blocking wrapper – call from non-async code (e.g. Streamlit).
    """
    fetcher = AsyncPageFetcher(base_domain=base_domain,
                               language_filter=language_filter)
    return asyncio.run(fetcher.fetch_all(urls))
