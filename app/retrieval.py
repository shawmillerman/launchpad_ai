"""Minimal retrieval placeholder.

For MVP you can swap this with FAISS or a simple cosine search over in-memory embeddings.
"""
from typing import List, Dict, Any, Tuple
import math


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def naive_retrieve(
    query_embedding: List[float],
    corpus: List[Dict[str, Any]],
    top_k: int = 5,
) -> List[Tuple[float, Dict[str, Any]]]:
    scored = []
    for rec in corpus:
        sim = cosine_similarity(query_embedding, rec.get("embedding", []))
        scored.append((sim, rec))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]
