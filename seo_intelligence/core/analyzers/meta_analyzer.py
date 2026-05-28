"""
core/analyzers/meta_analyzer.py
────────────────────────────────
Analyses Meta Title and Meta Description for every page.

Issues detected
───────────────
- missing_title
- missing_description
- title_too_short  / title_too_long
- description_too_short / description_too_long
- duplicate_title
- duplicate_description
"""

from __future__ import annotations

from collections import Counter
from typing import List

import pandas as pd

from config.settings import META
from database import db
from utils.logger import get_logger

log = get_logger(__name__)


class MetaAnalyzer:
    """
    Parameters
    ----------
    session_id : DB crawl session to analyse
    """

    def __init__(self, session_id: int):
        self.session_id = session_id
        self._pages: List[dict] = []

    # ─── Public API ───────────────────────────────────────────────────────────

    def run(self) -> pd.DataFrame:
        """
        Run full meta analysis.
        Returns a DataFrame with one row per issue.
        Also persists issues to DB.
        """
        self._pages = db.get_pages_for_session(self.session_id)
        if not self._pages:
            log.warning("No pages found for session %d", self.session_id)
            return pd.DataFrame()

        issues = []
        issues.extend(self._check_missing())
        issues.extend(self._check_lengths())
        issues.extend(self._check_duplicates())

        if issues:
            db.bulk_insert_meta_issues(issues)

        df = pd.DataFrame(issues)
        log.info("Meta analysis: %d issues found for session %d",
                 len(issues), self.session_id)
        return df

    # ─── Checks ───────────────────────────────────────────────────────────────

    def _check_missing(self) -> List[dict]:
        issues = []
        for page in self._pages:
            if not page.get("title"):
                issues.append(self._issue(page, "missing_title", None, "error"))
            if not page.get("meta_description"):
                issues.append(self._issue(page, "missing_description", None, "error"))
        return issues

    def _check_lengths(self) -> List[dict]:
        issues = []
        for page in self._pages:
            title = page.get("title") or ""
            desc  = page.get("meta_description") or ""

            if title:
                if len(title) < META["title_min"]:
                    issues.append(self._issue(page, "title_too_short", title, "warning"))
                elif len(title) > META["title_max"]:
                    issues.append(self._issue(page, "title_too_long", title, "warning"))

            if desc:
                if len(desc) < META["description_min"]:
                    issues.append(self._issue(page, "description_too_short", desc, "warning"))
                elif len(desc) > META["description_max"]:
                    issues.append(self._issue(page, "description_too_long", desc, "warning"))

        return issues

    def _check_duplicates(self) -> List[dict]:
        issues = []

        # Duplicate titles
        titles   = [p.get("title") or "" for p in self._pages]
        t_counts = Counter(t for t in titles if t)
        dup_titles = {t for t, c in t_counts.items() if c > 1}

        for page in self._pages:
            if page.get("title") in dup_titles:
                issues.append(self._issue(page, "duplicate_title",
                                          page["title"], "error"))

        # Duplicate descriptions
        descs    = [p.get("meta_description") or "" for p in self._pages]
        d_counts = Counter(d for d in descs if d)
        dup_descs = {d for d, c in d_counts.items() if c > 1}

        for page in self._pages:
            if page.get("meta_description") in dup_descs:
                issues.append(self._issue(page, "duplicate_description",
                                          page["meta_description"], "error"))

        return issues

    # ─── Helper ───────────────────────────────────────────────────────────────

    def _issue(self, page: dict, issue_type: str,
               value, severity: str) -> dict:
        return {
            "session_id": self.session_id,
            "page_id":    page["id"],
            "issue_type": issue_type,
            "value":      value,
            "severity":   severity,
            # extra fields for the DataFrame (not stored in DB)
            "_url":       page["url"],
        }


# ─── Stand-alone helper ───────────────────────────────────────────────────────

def run_meta_analysis(session_id: int) -> pd.DataFrame:
    return MetaAnalyzer(session_id).run()
