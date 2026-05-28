"""
core/nlp/anchor_analyzer.py
─────────────────────────────
Scores each anchor text against the context of its source page.

Algorithm
─────────
1. For each internal link: embed the anchor_text + embed the page body_text
2. Cosine similarity between anchor embedding and page embedding
3. Classify as:
   - "Relevant"            score >= NLP["anchor_relevance_high"]
   - "Partially Relevant"  NLP["anchor_relevance_low"] <= score < high
   - "Irrelevant"          score < NLP["anchor_relevance_low"]

Also detects:
  - Generic anchors  ("click here", "read more", "اضغط هنا", etc.)
  - Empty / very short anchors (< 3 chars)
"""

from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd

from config.settings import NLP
from core.nlp.embeddings import encode, cosine_similarity
from database import db
from utils.logger import get_logger

log = get_logger(__name__)

GENERIC_ANCHORS = {
    # English
    "click here", "here", "read more", "learn more", "this", "link",
    "page", "website", "visit", "more", "continue", "next", "source",
    # Arabic
    "اضغط هنا", "هنا", "اقرأ المزيد", "المزيد", "انقر", "الرابط",
    "تابع القراءة", "مصدر", "اطلع على",
}


class AnchorAnalyzer:

    def __init__(self, session_id: int):
        self.session_id = session_id

    def run(self) -> pd.DataFrame:
        pages = db.get_pages_for_session(self.session_id)
        links = db.get_links_for_session(self.session_id)

        if not links:
            log.warning("No internal links found for session %d", self.session_id)
            return pd.DataFrame()

        # Build page_id → body_text lookup
        page_map = {p["id"]: p for p in pages}

        # Get unique page texts to embed (avoid re-embedding same page multiple times)
        unique_page_ids  = list({lnk["source_page_id"] for lnk in links
                                  if lnk["source_page_id"] in page_map})
        page_texts       = [page_map[pid]["body_text"] or "" for pid in unique_page_ids]
        anchor_texts     = [lnk["anchor_text"] or "" for lnk in links]

        log.info("Encoding %d page texts and %d anchor texts …",
                 len(page_texts), len(anchor_texts))

        page_embeddings   = encode(page_texts, show_progress=True)
        anchor_embeddings = encode(anchor_texts, show_progress=True)

        # Map page_id → embedding index
        pid_to_idx = {pid: i for i, pid in enumerate(unique_page_ids)}

        rows = []
        update_data = []   # for DB update

        for i, lnk in enumerate(links):
            pid      = lnk["source_page_id"]
            anchor   = lnk["anchor_text"] or ""
            pg_idx   = pid_to_idx.get(pid)

            # ── Generic anchor detection ──────────────────────────────────────
            is_generic = anchor.lower().strip() in GENERIC_ANCHORS or len(anchor) < 3

            # ── Similarity score ──────────────────────────────────────────────
            if pg_idx is not None and anchor and not is_generic:
                score = cosine_similarity(anchor_embeddings[i], page_embeddings[pg_idx])
            else:
                score = 0.0

            # ── Classification ────────────────────────────────────────────────
            if is_generic:
                relevance = "Generic"
            elif score >= NLP["anchor_relevance_high"]:
                relevance = "Relevant"
            elif score >= NLP["anchor_relevance_low"]:
                relevance = "Partially Relevant"
            else:
                relevance = "Irrelevant"

            page = page_map.get(pid, {})
            rows.append({
                "source_url":       page.get("url", ""),
                "target_url":       lnk["target_url"],
                "anchor_text":      anchor,
                "relevance":        relevance,
                "relevance_score":  round(score, 4),
                "is_generic":       is_generic,
            })

            update_data.append({
                "source_page_id":   pid,
                "target_url":       lnk["target_url"],
                "anchor_text":      anchor,
                "anchor_relevance": relevance,
                "relevance_score":  round(score, 4),
            })

        df = pd.DataFrame(rows)
        log.info("Anchor analysis complete: %d links scored", len(df))

        # Persist updated scores back to DB
        _update_link_scores(self.session_id, update_data)

        return df


def _update_link_scores(session_id: int, data: List[dict]):
    """Update anchor_relevance and relevance_score in the DB."""
    from database.models import get_session_factory, InternalLink
    factory = get_session_factory()
    with factory() as s:
        for item in data:
            s.query(InternalLink).filter(
                InternalLink.session_id    == session_id,
                InternalLink.source_page_id == item["source_page_id"],
                InternalLink.target_url     == item["target_url"],
                InternalLink.anchor_text    == item["anchor_text"],
            ).update({
                "anchor_relevance": item["anchor_relevance"],
                "relevance_score":  item["relevance_score"],
            }, synchronize_session=False)
        s.commit()


def run_anchor_analysis(session_id: int) -> pd.DataFrame:
    return AnchorAnalyzer(session_id).run()
