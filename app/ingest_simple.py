"""
Simplified document ingestion for Phase 1.

Supports: PDF, DOCX, TXT files (no images, no OCR, no quality gates yet).
Focus: Load documents quickly and reliably.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)
from langchain_core.documents import Document


def load_documents_from_directory(
    path: str,
    supported_extensions: Optional[List[str]] = None,
) -> List[Document]:
    """
    Load documents from a directory.

    Args:
        path: Directory path to search
        supported_extensions: File extensions to load (default: .pdf, .docx, .txt)

    Returns:
        List of Document objects
    """
    if supported_extensions is None:
        supported_extensions = [".pdf", ".docx", ".txt"]

    documents = []
    base_path = Path(path)

    if not base_path.exists():
        return documents

    # Load PDFs
    if ".pdf" in supported_extensions:
        try:
            pdf_loader = DirectoryLoader(
                str(path), glob="**/*.pdf", loader_cls=PyPDFLoader, recursive=True
            )
            documents.extend(pdf_loader.load())
        except Exception as e:
            print(f"Warning: Failed to load PDFs: {e}")

    # Load DOCX
    if ".docx" in supported_extensions:
        try:
            docx_loader = DirectoryLoader(
                str(path), glob="**/*.docx", loader_cls=Docx2txtLoader, recursive=True
            )
            documents.extend(docx_loader.load())
        except Exception as e:
            print(f"Warning: Failed to load DOCX: {e}")

    # Load TXT
    if ".txt" in supported_extensions:
        try:
            txt_loader = DirectoryLoader(
                str(path), glob="**/*.txt", loader_cls=TextLoader, recursive=True
            )
            documents.extend(txt_loader.load())
        except Exception as e:
            print(f"Warning: Failed to load TXT: {e}")

    return documents


def load_single_document(file_path: str) -> Optional[Document]:
    """Load a single document by file extension."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() == ".pdf":
        loader = PyPDFLoader(file_path)
    elif path.suffix.lower() == ".docx":
        loader = Docx2txtLoader(file_path)
    elif path.suffix.lower() == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    docs = loader.load()
    return docs[0] if docs else None
