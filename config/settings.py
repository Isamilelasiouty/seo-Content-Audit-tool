"""
config/settings.py
──────────────────
Central configuration for the SEO Intelligence Tool.
All tuneable parameters live here – nothing is hard-coded in modules.
"""

from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent
DB_PATH    = BASE_DIR / "database" / "seo_intelligence.db"
LOG_DIR    = BASE_DIR / "logs"
EXPORT_DIR = BASE_DIR / "exports"

LOG_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)

# ─── Crawler ──────────────────────────────────────────────────────────────────
CRAWLER = {
    "max_concurrent_requests": 10,      # async semaphore limit
    "request_timeout":          20,      # seconds per request
    "retry_attempts":            3,
    "retry_delay":               2,      # seconds between retries
    "rate_limit_delay":          0.3,    # seconds between requests (per domain)
    "max_pages":             50_000,     # safety cap; set None for unlimited
    "respect_robots_txt":     True,
    "follow_redirects":       True,
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "SEOIntelligenceTool/1.0 (+https://github.com/your-repo)",
]

# ─── Meta Tag Thresholds ──────────────────────────────────────────────────────
META = {
    "title_min":        30,
    "title_max":        60,
    "description_min":  70,
    "description_max": 160,
}

# ─── Internal Link Density ───────────────────────────────────────────────────
LINK_DENSITY = {
    # words_range : suggested_internal_links
    "ranges": [
        (0,    300,  1,  2),
        (300,  600,  2,  4),
        (600,  1000, 3,  6),
        (1000, 1500, 5,  8),
        (1500, 2500, 7, 12),
        (2500, 9999, 10, 20),
    ]
}

# ─── NLP / Similarity ─────────────────────────────────────────────────────────
NLP = {
    # Sentence-transformers model – multilingual supports Arabic + English
    "embedding_model":    "paraphrase-multilingual-MiniLM-L12-v2",
    "similarity_threshold_cluster":   0.75,   # cosine sim to group pages
    "similarity_threshold_duplicate": 0.92,   # near-duplicate threshold
    "anchor_relevance_high":          0.65,
    "anchor_relevance_low":           0.35,
}

# ─── Supported Languages ──────────────────────────────────────────────────────
SUPPORTED_LANGUAGES = {
    "ar": "العربية",
    "en": "English",
    "auto": "Auto-detect",
}

# ─── Database ─────────────────────────────────────────────────────────────────
DATABASE = {
    "url": f"sqlite:///{DB_PATH}",
    # Switch to PostgreSQL:  "postgresql+psycopg2://user:pass@host/dbname"
}
