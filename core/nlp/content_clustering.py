"""
core/nlp/content_clustering.py
────────────────────────────────
Groups pages into semantic clusters using:
  • Sentence Transformer embeddings (multilingual)
  • Agglomerative Clustering (scikit-learn)

Output
──────
  DataFrame with columns: url, cluster_id, cluster_name, centroid_distance
  Also persists clusters to DB.
"""

from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity as sk_cosine

from config.settings import NLP
from core.nlp.embeddings import encode
from database import db
from utils.logger import get_logger

log = get_logger(__name__)


class ContentClusteringEngine:

    def __init__(self, session_id: int):
        self.session_id = session_id

    def run(self) -> pd.DataFrame:
        pages = db.get_pages_for_session(self.session_id)
        if not pages:
            return pd.DataFrame()

        # Use title + h1 as the text for clustering (fast, representative)
        texts = []
        for p in pages:
            parts = [p.get("title") or "", p.get("h1") or ""]
            texts.append(" ".join(filter(None, parts)))

        log.info("Clustering %d pages …", len(pages))
        embeddings = encode(texts, show_progress=True)

        # Dynamic cluster count: sqrt(n) is a reasonable heuristic
        n_clusters = max(2, int(len(pages) ** 0.5))
        n_clusters = min(n_clusters, 200)   # cap at 200 topic groups

        clustering = AgglomerativeClustering(
            n_clusters=n_clusters,
            metric="cosine",
            linkage="average",
        )
        labels = clustering.fit_predict(embeddings)

        # ── Build DataFrame ───────────────────────────────────────────────────
        rows = []
        for i, page in enumerate(pages):
            rows.append({
                "page_id":    page["id"],
                "url":        page["url"],
                "title":      page.get("title") or "",
                "cluster_id": int(labels[i]),
            })
        df = pd.DataFrame(rows)

        # ── Cluster names: pick the most central title as the group name ──────
        cluster_names = self._name_clusters(df, embeddings, labels)
        df["cluster_name"] = df["cluster_id"].map(cluster_names)

        # ── Persist ───────────────────────────────────────────────────────────
        self._persist_clusters(df)

        log.info("Clustering done: %d clusters", n_clusters)
        return df

    def _name_clusters(self, df: pd.DataFrame, embeddings: np.ndarray,
                       labels: np.ndarray) -> dict:
        """Name each cluster by the title closest to its centroid."""
        cluster_names = {}
        for cid in np.unique(labels):
            idx = np.where(labels == cid)[0]
            cluster_embs = embeddings[idx]
            centroid = cluster_embs.mean(axis=0, keepdims=True)
            sims     = sk_cosine(centroid, cluster_embs)[0]
            best     = idx[sims.argmax()]
            cluster_names[int(cid)] = df.iloc[best]["title"] or f"Cluster {cid}"
        return cluster_names

    def _persist_clusters(self, df: pd.DataFrame):
        cluster_data = []
        for cid, group in df.groupby("cluster_id"):
            page_ids = group["page_id"].tolist()
            # centroid URL = first page in group
            centroid = group.iloc[0]["url"]
            name     = group.iloc[0]["cluster_name"]
            cluster_data.append({
                "session_id":   self.session_id,
                "cluster_name": name,
                "page_ids":     page_ids,
                "centroid_url": centroid,
            })
        db.save_clusters(cluster_data)


def run_content_clustering(session_id: int) -> pd.DataFrame:
    return ContentClusteringEngine(session_id).run()
