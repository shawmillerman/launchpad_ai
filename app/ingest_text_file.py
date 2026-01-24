from pathlib import Path
from typing import Any, Dict, List, Optional

from .chunking import split_by_tokens
from .embed import embed_texts


def ingest_txt_file(
    path: str,
    base_metadata: Optional[Dict[str, Any]] = None,
    max_tokens: int = 500,
    overlap: int = 100,
) -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Missing file: {p}")

    text = p.read_text(encoding="utf-8", errors="ignore").strip()
    if not text:
        raise ValueError(f"File is empty: {p}")

    chunks = split_by_tokens(text, max_tokens=max_tokens, overlap=overlap)
    embeddings = embed_texts(chunks)

    records: List[Dict[str, Any]] = []
    base_metadata = base_metadata or {}
    for i, chunk in enumerate(chunks):
        md = dict(base_metadata)
        md["chunk_index"] = i
        records.append({"chunk": chunk, "embedding": embeddings[i], "metadata": md})
    return records
