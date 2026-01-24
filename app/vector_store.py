"""Minimal FAISS helper for MVP.

Stores vectors with associated records (chunk + metadata).
If FAISS is unavailable, you can swap to naive retrieval.
"""
from typing import List, Dict, Any, Tuple
import numpy as np
import faiss


def build_index(records: List[Dict[str, Any]]) -> Tuple[faiss.IndexFlatIP, List[Dict[str, Any]]]:
    """Build a FAISS inner-product index from records with `embedding` key.

    Returns the index and a parallel list of records aligned by row id.
    """
    if not records:
        raise ValueError("No records to index")

    vectors = np.array([rec["embedding"] for rec in records], dtype="float32")
    index = faiss.IndexFlatIP(vectors.shape[1])
    faiss.normalize_L2(vectors)
    index.add(vectors)
    return index, records


def search(
    index: faiss.IndexFlatIP,
    records: List[Dict[str, Any]],
    query_embedding: List[float],
    top_k: int = 5,
) -> List[Tuple[float, Dict[str, Any]]]:
    """Return top_k (score, record) pairs."""
    q = np.array([query_embedding], dtype="float32")
    faiss.normalize_L2(q)
    scores, idxs = index.search(q, top_k)
    out: List[Tuple[float, Dict[str, Any]]] = []
    for score, idx in zip(scores[0], idxs[0]):
        if idx == -1:
            continue
        out.append((float(score), records[idx]))
    return out
