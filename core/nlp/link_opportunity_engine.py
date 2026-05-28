"""
core/nlp/link_opportunity_engine.py
─────────────────────────────────────
Finds missing internal link opportunities.

Algorithm
─────────
1. Embed every page (title + h1 + first 500 words of body)
2. For each page A, find top-K similar pages B
3. If B is NOT already linked from A → it's an opportunity
4. Suggest the most relevant noun phrase from B's title as anchor text

Returns a DataFrame of suggestions.
"""

from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd

from config.settings import NLP
from core.nlp.embeddings import encode, batch_cosine_matrix
from database import db
from utils.logger import get_logger

log = get_logger(__name__)

TOP_K_SUGGESTIONS = 5   # max suggestions per page


class LinkOpportunityEngine:

    def __init__(self, session_id: int):
        self.session_id = session_id

    def run(self) -> pd.DataFrame:
        pages = db.get_pages_for_session(self.session_id)
        links = db.get_links_for_session(self.session_id)

        if not pages:
            return pd.DataFrame()

        # Build existing link map: source_url → set of target_urls
        existing: dict[str, set] = {}
        for lnk in links:
            # We need source URL; look up from pages
            pass

        # Rebuild with source URL
        page_id_to_url = {p["id"]: p["url"] for p in pages}
        for lnk in links:
            src_url = page_id_to_url.get(lnk["source_page_id"], "")
            existing.setdefault(src_url, set()).add(lnk["target_url"])

        # Embed pages
        texts = []
        for p in pages:
            snippet = " ".join(filter(None, [
                p.get("title") or "",
                p.get("h1")    or "",
                (p.get("body_text") or "")[:500],
            ]))
            texts.append(snippet)

        log.info("Encoding %d pages for link opportunity analysis …", len(pages))
        embeddings = encode(texts, show_progress=True)
        sim_matrix = batch_cosine_matrix(embeddings)
        np.fill_diagonal(sim_matrix, 0)   # ignore self-similarity

        threshold = NLP["similarity_threshold_cluster"]
        rows = []

        for i, page_a in enumerate(pages):
            src_url = page_a["url"]
            already_linked = existing.get(src_url, set())

            # Get top-K similar pages above threshold
            sims = sim_matrix[i]
            top_indices = np.argsort(sims)[::-1]

            added = 0
            for j in top_indices:
                if added >= TOP_K_SUGGESTIONS:
                    break
                score = float(sims[j])
                if score < threshold:
                    break

                page_b   = pages[j]
                tgt_url  = page_b["url"]
                if tgt_url == src_url:
                    continue
                if tgt_url in already_linked:
                    continue

                # Suggested anchor = page_b's title (or H1)
                suggested_anchor = page_b.get("title") or page_b.get("h1") or tgt_url

                rows.append({
                    "source_url":        src_url,
                    "source_title":      page_a.get("title") or "",
                    "target_url":        tgt_url,
                    "target_title":      page_b.get("title") or "",
                    "suggested_anchor":  suggested_anchor,
                    "similarity_score":  round(score, 4),
                })
                added += 1

        df = pd.DataFrame(rows)

        # Persist
        if not df.empty:
            opp_data = []
            url_to_id = {p["url"]: p["id"] for p in pages}
            for _, row in df.iterrows():
                src_id = url_to_id.get(row["source_url"])
                if src_id:
                    opp_data.append({
                        "session_id":       self.session_id,
                        "source_page_id":   src_id,
                        "target_url":       row["target_url"],
                        "suggested_anchor": row["suggested_anchor"],
                        "similarity_score": row["similarity_score"],
                    })
            db.save_opportunities(opp_data)

        log.info("Link opportunities: %d suggestions found", len(df))
        return df


def run_link_opportunity_analysis(session_id: int) -> pd.DataFrame:
    return LinkOpportunityEngine(session_id).run()
