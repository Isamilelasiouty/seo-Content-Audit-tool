"""
core/analyzers/link_density_analyzer.py
─────────────────────────────────────────
Calculates Internal Link Density for every page.

Metrics produced
────────────────
- internal_link_count     : actual number of internal links on the page
- word_count              : words on the page
- link_density_ratio      : links / (words / 100)  — links per 100 words
- suggested_min_links     : lower bound from config ranges
- suggested_max_links     : upper bound from config ranges
- density_status          : "optimal" | "under_linked" | "over_linked"
"""

from __future__ import annotations

from typing import List

import pandas as pd

from config.settings import LINK_DENSITY
from database import db
from utils.logger import get_logger

log = get_logger(__name__)


def _lookup_suggested(word_count: int):
    for (wmin, wmax, lmin, lmax) in LINK_DENSITY["ranges"]:
        if wmin <= word_count < wmax:
            return lmin, lmax
    # fallback for very long pages
    return 10, 20


class LinkDensityAnalyzer:

    def __init__(self, session_id: int):
        self.session_id = session_id

    def run(self) -> pd.DataFrame:
        pages = db.get_pages_for_session(self.session_id)
        links = db.get_links_for_session(self.session_id)

        # Count links per source page
        link_count_map: dict[int, int] = {}
        for lnk in links:
            pid = lnk["source_page_id"]
            link_count_map[pid] = link_count_map.get(pid, 0) + 1

        rows = []
        for page in pages:
            wc       = page.get("word_count") or 0
            lc       = link_count_map.get(page["id"], 0)
            ratio    = round(lc / (wc / 100), 2) if wc >= 50 else 0.0
            smin, smax = _lookup_suggested(wc)

            if lc < smin:
                status = "under_linked"
            elif lc > smax:
                status = "over_linked"
            else:
                status = "optimal"

            rows.append({
                "url":                   page["url"],
                "word_count":            wc,
                "internal_link_count":   lc,
                "link_density_ratio":    ratio,
                "suggested_min_links":   smin,
                "suggested_max_links":   smax,
                "density_status":        status,
            })

        df = pd.DataFrame(rows)
        log.info("Link density analysis: %d pages", len(df))
        return df


def run_link_density_analysis(session_id: int) -> pd.DataFrame:
    return LinkDensityAnalyzer(session_id).run()
