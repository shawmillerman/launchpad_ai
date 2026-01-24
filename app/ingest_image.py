"""Image OCR ingest using Tesseract.

Requires:
- pytesseract
- pillow
- Tesseract installed on system (e.g., `brew install tesseract` on macOS)
"""
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytesseract
from PIL import Image

from .chunking import split_by_tokens
from .embed import embed_texts


def ocr_image(path: str) -> str:
    if not Path(path).exists():
        raise FileNotFoundError(f"Missing image file: {path}")
    img = Image.open(path)
    return pytesseract.image_to_string(img)


def ingest_image(
    path: str,
    base_metadata: Optional[Dict[str, Any]] = None,
    max_tokens: int = 500,
    overlap: int = 100,
) -> List[Dict[str, Any]]:
    base_metadata = base_metadata or {}
    raw_text = ocr_image(path)
    text = raw_text.strip()
    if not text:
        raise ValueError(f"No OCR text extracted from {path}")

    chunks = split_by_tokens(text, max_tokens=max_tokens, overlap=overlap)
    embeddings = embed_texts(chunks)

    records: List[Dict[str, Any]] = []
    for i, chunk in enumerate(chunks):
        md = dict(base_metadata)
        md["chunk_index"] = i
        md["source_type"] = "image_ocr"
        md["source_file"] = Path(path).name
        records.append({"chunk": chunk, "embedding": embeddings[i], "metadata": md})
    return records
