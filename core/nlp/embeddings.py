"""
core/nlp/embeddings.py
───────────────────────
Lightweight wrapper around sentence-transformers.

Loads the multilingual model once (cached) and exposes:
  - encode(texts) → numpy array of embeddings
  - cosine_similarity(a, b) → float in [0, 1]
  - batch_cosine_matrix(embeddings) → NxN similarity matrix
"""

from __future__ import annotations

import numpy as np
from functools import lru_cache
from typing import List, Union

from config.settings import NLP
from utils.logger import get_logger

log = get_logger(__name__)


@lru_cache(maxsize=1)
def _load_model():
    """Load model once and cache in memory."""
    from sentence_transformers import SentenceTransformer
    model_name = NLP["embedding_model"]
    log.info("Loading sentence-transformer model: %s", model_name)
    model = SentenceTransformer(model_name)
    log.info("Model loaded ✓")
    return model


def encode(texts: List[str], batch_size: int = 64,
           show_progress: bool = False) -> np.ndarray:
    """
    Encode a list of strings to embeddings.

    Parameters
    ----------
    texts         : List of strings (Arabic or English or mixed)
    batch_size    : Encoding batch size (tune based on available RAM)
    show_progress : Show tqdm progress bar

    Returns
    -------
    np.ndarray of shape (N, embedding_dim)
    """
    model = _load_model()
    # Truncate very long texts to avoid OOM
    texts = [t[:2000] if t else "" for t in texts]
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
        normalize_embeddings=True,   # L2-norm → cosine = dot product
    )
    return embeddings


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Cosine similarity between two normalised vectors (fast, no sklearn needed)."""
    return float(np.dot(vec_a, vec_b))


def batch_cosine_matrix(embeddings: np.ndarray) -> np.ndarray:
    """
    Compute NxN cosine similarity matrix for all embeddings.
    Since embeddings are L2-normalised, this is just a matrix product.
    """
    return np.dot(embeddings, embeddings.T)


def top_similar_pairs(
    embeddings: np.ndarray,
    ids: List[int],
    threshold: float = 0.75,
    top_k: int = 5,
) -> List[dict]:
    """
    Return all pairs above *threshold*, sorted by similarity desc.
    Avoids double-counting (i < j only).

    Returns list of {"id_a", "id_b", "score"}.
    """
    matrix = batch_cosine_matrix(embeddings)
    n      = len(ids)
    pairs  = []

    for i in range(n):
        # vectorised: find all j > i where sim >= threshold
        sims = matrix[i, i+1:]
        above = np.where(sims >= threshold)[0] + i + 1
        for j in above:
            pairs.append({
                "id_a":  ids[i],
                "id_b":  ids[j],
                "score": float(matrix[i, j]),
            })

    pairs.sort(key=lambda x: x["score"], reverse=True)
    return pairs
