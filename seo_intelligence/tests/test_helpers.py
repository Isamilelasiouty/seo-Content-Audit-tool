"""
tests/test_helpers.py
──────────────────────
Basic unit tests for utility functions.
Run with: pytest tests/
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.helpers import (
    normalise_url, is_internal_url, resolve_url,
    clean_text, count_words, get_domain,
)


def test_normalise_url():
    assert normalise_url("HTTPS://EXAMPLE.COM/Page/") == "https://example.com/Page"
    assert normalise_url("http://example.com:80/path") == "http://example.com/path"


def test_is_internal_url():
    assert is_internal_url("https://example.com/page", "example.com")
    assert not is_internal_url("https://other.com/page", "example.com")


def test_resolve_url():
    result = resolve_url("/about", "https://example.com")
    assert result == "https://example.com/about"

    result = resolve_url("https://other.com", "https://example.com")
    assert result == "https://other.com"


def test_clean_text():
    assert clean_text("  hello   world  ") == "hello world"
    assert clean_text("") == ""


def test_count_words():
    assert count_words("hello world test") == 3
    assert count_words("مرحبا بالعالم") == 2
    assert count_words("") == 0


def test_get_domain():
    assert get_domain("https://www.example.com/page") == "example.com"
    assert get_domain("https://blog.example.com") == "blog.example.com"
