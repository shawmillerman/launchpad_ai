from typing import Any, Dict, List, Optional
from pathlib import Path
from pypdf import PdfReader

from .chunking import split_by_tokens
from .docx_reader import read_docx_with_headings
from .embed import embed_texts


def read_pdf_plaintext(path: str) -> str:
    reader = PdfReader(path)
    text_parts: List[str] = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)


def ingest_pdf(
    path: str,
    base_metadata: Optional[Dict[str, Any]] = None,
    max_tokens: int = 500,
    overlap: int = 100,
) -> List[Dict[str, Any]]:
    base_metadata = base_metadata or {}
    raw_text = read_pdf_plaintext(path)
    chunks = split_by_tokens(raw_text, max_tokens=max_tokens, overlap=overlap)
    embeddings = embed_texts(chunks)

    records: List[Dict[str, Any]] = []
    for i, chunk in enumerate(chunks):
        md = dict(base_metadata)
        md["chunk_index"] = i
        records.append({"chunk": chunk, "embedding": embeddings[i], "metadata": md})
    return records


def ingest_docx(
    path: str,
    base_metadata: Optional[Dict[str, Any]] = None,
    max_tokens: int = 500,
    overlap: int = 100,
) -> List[Dict[str, Any]]:
    base_metadata = base_metadata or {}
    chunks, heading_metadatas = read_docx_with_headings(path)
    # Optionally re-chunk long paragraphs if needed
    final_chunks: List[str] = []
    final_metas: List[Dict[str, Any]] = []
    for chunk, hmeta in zip(chunks, heading_metadatas):
        sub_chunks = split_by_tokens(chunk, max_tokens=max_tokens, overlap=overlap)
        for sub_chunk in sub_chunks:
            final_chunks.append(sub_chunk)
            md = dict(base_metadata)
            md.update(hmeta)
            final_metas.append(md)

    embeddings = embed_texts(final_chunks)
    records: List[Dict[str, Any]] = []
    for i, chunk in enumerate(final_chunks):
        md = dict(final_metas[i])
        md["chunk_index"] = i
        records.append({"chunk": chunk, "embedding": embeddings[i], "metadata": md})
    return records


def ingest_by_extension(
    path: str,
    base_metadata: Optional[Dict[str, Any]] = None,
    max_tokens: int = 500,
    overlap: int = 100,
) -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Missing file: {p}")

    if path.lower().endswith(".pdf"):
        return ingest_pdf(path, base_metadata=base_metadata, max_tokens=max_tokens, overlap=overlap)
    if path.lower().endswith(".docx"):
        return ingest_docx(path, base_metadata=base_metadata, max_tokens=max_tokens, overlap=overlap)
    if path.lower().endswith(".txt"):
        from .ingest_text_file import ingest_txt_file

        return ingest_txt_file(path, base_metadata=base_metadata, max_tokens=max_tokens, overlap=overlap)

    raise ValueError(f"Unsupported file format: {path}. Expected .pdf, .docx, or .txt")
