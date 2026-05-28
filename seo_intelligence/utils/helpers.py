"""
utils/helpers.py
────────────────
Shared helper functions used across multiple modules.
"""

import re
import unicodedata
from urllib.parse import urljoin, urlparse, urlunparse
from typing import Optional
import random

from config.settings import USER_AGENTS


# ─── URL helpers ─────────────────────────────────────────────────────────────

def normalise_url(url: str) -> str:
    """Lowercase scheme+host, remove default port, strip trailing slash."""
    try:
        p = urlparse(url.strip())
        netloc = p.netloc.lower()
        # remove default ports
        netloc = re.sub(r":80$", "", netloc)
        netloc = re.sub(r":443$", "", netloc)
        path = p.path.rstrip("/") or "/"
        return urlunparse((p.scheme.lower(), netloc, path, p.params, p.query, ""))
    except Exception:
        return url


def is_internal_url(url: str, base_domain: str) -> bool:
    """Return True if *url* belongs to *base_domain*."""
    try:
        return urlparse(url).netloc.lower().lstrip("www.") == base_domain.lstrip("www.")
    except Exception:
        return False


def resolve_url(href: str, base_url: str) -> Optional[str]:
    """Convert a relative href to an absolute URL."""
    try:
        resolved = urljoin(base_url, href)
        p = urlparse(resolved)
        if p.scheme in ("http", "https"):
            return normalise_url(resolved)
    except Exception:
        pass
    return None


def get_domain(url: str) -> str:
    return urlparse(url).netloc.lower().lstrip("www.")


# ─── Text helpers ─────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Normalise whitespace and strip invisible characters."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def count_words(text: str) -> int:
    """Word count that handles Arabic and Latin text."""
    if not text:
        return 0
    return len(text.split())


def truncate(text: str, max_len: int = 120) -> str:
    """Truncate text for display."""
    return text[:max_len] + "…" if len(text) > max_len else text


# ─── HTTP helpers ─────────────────────────────────────────────────────────────

def random_user_agent() -> str:
    return random.choice(USER_AGENTS)


def build_headers(extra: Optional[dict] = None) -> dict:
    headers = {
        "User-Agent": random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5,ar;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    if extra:
        headers.update(extra)
    return headers
