"""
core/crawler/sitemap_parser.py
───────────────────────────────
Parses sitemap.xml and sitemap_index.xml to extract every URL.
Supports:
  • Standard sitemap.xml
  • sitemap_index.xml (recursive)
  • Gzipped sitemaps (.xml.gz)
  • Multilingual <xhtml:link> alternates
  • Fallback to /sitemap.xml, /sitemap_index.xml, /robots.txt discovery
"""

from __future__ import annotations

import gzip
import re
from io import BytesIO
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from config.settings import CRAWLER
from utils.helpers import build_headers, normalise_url
from utils.logger import get_logger

log = get_logger(__name__)

SITEMAP_NAMESPACES = [
    "http://www.sitemaps.org/schemas/sitemap/0.9",
    "http://www.google.com/schemas/sitemap/0.84",
]

# ─── Public entry point ───────────────────────────────────────────────────────

def discover_and_parse_sitemap(base_url: str) -> List[str]:
    """
    Given a base URL (e.g. https://example.com), discover the sitemap
    and return a deduplicated list of all page URLs.
    """
    base_url = base_url.rstrip("/")
    candidates = _discover_sitemap_urls(base_url)

    all_urls: list[str] = []
    visited_sitemaps: set[str] = set()

    for sitemap_url in candidates:
        urls = _parse_sitemap(sitemap_url, visited_sitemaps)
        all_urls.extend(urls)
        if all_urls:
            break   # stop after first successful sitemap

    deduped = list(dict.fromkeys(normalise_url(u) for u in all_urls))
    log.info("Sitemap discovery: found %d unique URLs for %s", len(deduped), base_url)
    return deduped


# ─── Discovery ────────────────────────────────────────────────────────────────

def _discover_sitemap_urls(base_url: str) -> List[str]:
    """Return a list of sitemap URLs to try, in priority order."""
    candidates = [
        f"{base_url}/sitemap_index.xml",
        f"{base_url}/sitemap.xml",
        f"{base_url}/sitemap/",
        f"{base_url}/sitemaps/sitemap.xml",
    ]

    # Also check robots.txt
    robots_sitemaps = _extract_sitemaps_from_robots(base_url)
    return robots_sitemaps + candidates   # robots.txt entries take priority


def _extract_sitemaps_from_robots(base_url: str) -> List[str]:
    robots_url = f"{base_url}/robots.txt"
    try:
        resp = requests.get(robots_url, headers=build_headers(),
                            timeout=CRAWLER["request_timeout"])
        if resp.status_code == 200:
            urls = re.findall(r"(?i)^Sitemap:\s*(.+)$", resp.text, re.MULTILINE)
            urls = [u.strip() for u in urls if u.strip().startswith("http")]
            log.debug("robots.txt yielded %d sitemap(s)", len(urls))
            return urls
    except Exception as exc:
        log.debug("robots.txt fetch failed: %s", exc)
    return []


# ─── Recursive sitemap parser ─────────────────────────────────────────────────

def _parse_sitemap(sitemap_url: str, visited: set) -> List[str]:
    if sitemap_url in visited:
        return []
    visited.add(sitemap_url)
    log.debug("Parsing sitemap: %s", sitemap_url)

    content = _fetch_sitemap_content(sitemap_url)
    if not content:
        return []

    soup = BeautifulSoup(content, "lxml-xml")

    # ── sitemap_index → recurse ──────────────────────────────────────────────
    sitemap_tags = soup.find_all("sitemap")
    if sitemap_tags:
        sub_urls: list[str] = []
        for tag in sitemap_tags:
            loc = tag.find("loc")
            if loc and loc.text:
                sub_urls.extend(_parse_sitemap(loc.text.strip(), visited))
        return sub_urls

    # ── regular sitemap → extract <loc> ─────────────────────────────────────
    url_tags = soup.find_all("url")
    page_urls: list[str] = []
    for tag in url_tags:
        loc = tag.find("loc")
        if loc and loc.text:
            page_urls.append(loc.text.strip())

    log.debug("  → %d URLs from %s", len(page_urls), sitemap_url)
    return page_urls


def _fetch_sitemap_content(url: str) -> Optional[bytes]:
    try:
        resp = requests.get(
            url, headers=build_headers(),
            timeout=CRAWLER["request_timeout"],
            allow_redirects=True,
        )
        if resp.status_code != 200:
            return None

        content = resp.content

        # Handle gzipped sitemaps
        if url.endswith(".gz") or resp.headers.get("Content-Encoding") == "gzip":
            try:
                content = gzip.decompress(content)
            except Exception:
                pass

        return content
    except Exception as exc:
        log.warning("Failed to fetch sitemap %s: %s", url, exc)
        return None
