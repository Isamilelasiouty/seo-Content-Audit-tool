"""
core/nlp/duplicate_detector.py
────────────────────────────────
Detects duplicate and near-duplicate pages using:
  • Exact title duplicates
  • TF-IDF cosine similarity on body text  (fast for large corpora)
  • Sentence embedding similarity  (more accurate, for top candidates)

Returns a DataFrame of pairs with their similarity score and type.
"""

from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sk_cosine

from config.settings import NLP
from core.nlp.embeddings import encode, top_similar_pairs
from database import db
from utils.logger import get_logger

log = get_logger(__name__)


class DuplicateDetector:

    def __init__(self, session_id: int):
        self.session_id = session_id

    def run(self) -> pd.DataFrame:
        pages = db.get_pages_for_session(self.session_id)
        if not pages:
            return pd.DataFrame()

        id_map  = {p["id"]: p for p in pages}
        results = []

        # ── 1. Exact title duplicates ─────────────────────────────────────────
        title_groups: dict[str, list] = {}
        for p in pages:
            t = (p.get("title") or "").strip().lower()
            if t:
                title_groups.setdefault(t, []).append(p["id"])

        for t, ids in title_groups.items():
            if len(ids) > 1:
                for i in range(len(ids)):
                    for j in range(i + 1, len(ids)):
                        results.append({
                            "url_a":          id_map[ids[i]]["url"],
                            "url_b":          id_map[ids[j]]["url"],
                            "similarity_score": 1.0,
                            "duplicate_type": "title_duplicate",
                        })

        # ── 2. TF-IDF near-duplicates ─────────────────────────────────────────
        texts = [p.get("body_text") or "" for p in pages]
        page_ids = [p["id"] for p in pages]
        tfidf_pairs = self._tfidf_duplicates(texts, page_ids, id_map)
        results.extend(tfidf_pairs)

        # ── 3. Embedding near-duplicates (on body text) ───────────────────────
        log.info("Running embedding duplicate detection on %d pages …", len(pages))
        embeddings = encode(texts, show_progress=True)
        emb_pairs  = top_similar_pairs(
            embeddings, page_ids,
            threshold=NLP["similarity_threshold_duplicate"]
        )
        for pair in emb_pairs:
            results.append({
                "url_a":            id_map[pair["id_a"]]["url"],
                "url_b":            id_map[pair["id_b"]]["url"],
                "similarity_score": round(pair["score"], 4),
                "duplicate_type":   "near_duplicate",
            })

        # Deduplicate the results list itself
        seen = set()
        unique_results = []
        for r in results:
            key = tuple(sorted([r["url_a"], r["url_b"]]))
            if key not in seen:
                seen.add(key)
                unique_results.append(r)

        df = pd.DataFrame(unique_results)

        # Persist to DB
        if not df.empty:
            dup_data = []
            for p in pages:
                pass   # we need page_ids for DB — handled below

            # Quick id lookup
            url_to_id = {p["url"]: p["id"] for p in pages}
            db_rows = []
            for r in unique_results:
                a_id = url_to_id.get(r["url_a"])
                b_id = url_to_id.get(r["url_b"])
                if a_id and b_id:
                    db_rows.append({
                        "session_id":      self.session_id,
                        "page_a_id":       a_id,
                        "page_b_id":       b_id,
                        "similarity_score": r["similarity_score"],
                        "duplicate_type":  r["duplicate_type"],
                    })
            if db_rows:
                db.save_duplicates(db_rows)

        log.info("Duplicate detection: %d pairs found", len(df))
        return df

    def _tfidf_duplicates(self, texts: List[str], page_ids: List[int],
                          id_map: dict) -> List[dict]:
        try:
            vec = TfidfVectorizer(
                max_features=10_000,
                min_df=2,
                ngram_range=(1, 2),
            )
            matrix = vec.fit_transform(texts)
        except Exception as exc:
            log.warning("TF-IDF failed: %s", exc)
            return []

        # Compute similarity in chunks to save memory
        threshold = NLP["similarity_threshold_duplicate"]
        n = len(page_ids)
        chunk = 500
        pairs = []

        for start in range(0, n, chunk):
            end    = min(start + chunk, n)
            sim    = sk_cosine(matrix[start:end], matrix)
            for local_i, global_i in enumerate(range(start, end)):
                row = sim[local_i]
                above = np.where(row > threshold)[0]
                for j in above:
                    if j <= global_i:
                        continue
                    pairs.append({
                        "url_a":            id_map[page_ids[global_i]]["url"],
                        "url_b":            id_map[page_ids[j]]["url"],
                        "similarity_score": round(float(row[j]), 4),
                        "duplicate_type":   "near_duplicate_tfidf",
                    })

        return pairs


def run_duplicate_detection(session_id: int) -> pd.DataFrame:
    return DuplicateDetector(session_id).run()
