from typing import Any, Dict, List, Optional
from pathlib import Path
from pypdf import PdfReader

from .chunking import split_by_tokens
from .docx_reader import read_docx_with_headings
from .embed import embed_texts
from .quality import apply_quality_gates


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


_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}


def ingest_image(
    path: str,
    base_metadata: Optional[Dict[str, Any]] = None,
    max_tokens: int = 500,
    overlap: int = 100,
) -> List[Dict[str, Any]]:
    from .ingest_image import ImageIngestionPipeline

    base_metadata = base_metadata or {}
    pipeline = ImageIngestionPipeline()
    result = pipeline.extract_text(path)

    text = (result.get("content") or "").strip()
    extraction_warnings: List[str] = (
        result.get("metadata", {})
        .get("quality_signals", {})
        .get("extraction_warnings", [])
    )

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
        md["extraction_warnings"] = list(extraction_warnings)
        records.append({"chunk": chunk, "embedding": embeddings[i], "metadata": md})
    return records


def ingest_by_extension(
    path: str,
    base_metadata: Optional[Dict[str, Any]] = None,
    max_tokens: int = 500,
    overlap: int = 100,
    strict_quality: bool = False,
) -> List[Dict[str, Any]]:
    """Ingest a document by detecting its format from the file extension.

    Args:
        path: Path to the source file.
        base_metadata: Key/value pairs merged into every record's metadata.
        max_tokens: Maximum chunk size in tokens.
        overlap: Token overlap between consecutive chunks.
        strict_quality: When True, raise ValueError if the quality gate
            returns NEEDS_REVIEW instead of silently tagging records.

    Returns:
        List of chunk records, each carrying ``quality_status`` and
        ``quality_reasons`` in its metadata.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Missing file: {p}")

    if path.lower().endswith(".pdf"):
        records = ingest_pdf(path, base_metadata=base_metadata, max_tokens=max_tokens, overlap=overlap)
    elif path.lower().endswith(".docx"):
        records = ingest_docx(path, base_metadata=base_metadata, max_tokens=max_tokens, overlap=overlap)
    elif path.lower().endswith(".txt"):
        from .ingest_text_file import ingest_txt_file
        records = ingest_txt_file(path, base_metadata=base_metadata, max_tokens=max_tokens, overlap=overlap)
    elif p.suffix.lower() in _IMAGE_EXTENSIONS:
        records = ingest_image(path, base_metadata=base_metadata, max_tokens=max_tokens, overlap=overlap)
    else:
        supported = ".pdf, .docx, .txt, " + ", ".join(sorted(_IMAGE_EXTENSIONS))
        raise ValueError(f"Unsupported file format: {path}. Expected one of: {supported}")

    # --- Quality gate ---
    # Reconstruct document text from chunks and collect any extraction warnings
    # already present in the first record (set by OCR / format parsers).
    joined_text = " ".join(r["chunk"] for r in records)
    extraction_warnings: List[str] = records[0]["metadata"].get("extraction_warnings", []) if records else []
    quality = apply_quality_gates(
        raw_text=joined_text,
        cleaned_text=joined_text,
        extraction_warnings=extraction_warnings,
    )

    if strict_quality and not quality.passed:
        raise ValueError(
            f"Quality gate failed for {path}: {quality.reasons}"
        )

    for record in records:
        record["metadata"]["quality_status"] = quality.status
        record["metadata"]["quality_reasons"] = quality.reasons

    return records
