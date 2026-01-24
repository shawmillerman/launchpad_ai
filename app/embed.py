"""Minimal embedding helper with provider switch (OpenAI or Gemini).

Set env vars:
- EMBED_PROVIDER=openai|gemini (default: openai)
- OPENAI_API_KEY (if openai)
- GEMINI_API_KEY (if gemini)
- OPENAI_EMBED_MODEL (default: text-embedding-3-small)
- GEMINI_EMBED_MODEL (default: embedding-001)
"""

import os
from typing import List


PROVIDER = os.getenv("EMBED_PROVIDER", "openai").lower()
OPENAI_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
GEMINI_MODEL = os.getenv("GEMINI_EMBED_MODEL", "models/embedding-001")


def _embed_openai(texts: List[str]) -> List[List[float]]:
    import openai

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required when EMBED_PROVIDER=openai")

    openai.api_key = api_key
    resp = openai.embeddings.create(model=OPENAI_MODEL, input=texts)
    return [d.embedding for d in resp.data]


def _embed_gemini(texts: List[str]) -> List[List[float]]:
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is required when EMBED_PROVIDER=gemini")

    genai.configure(api_key=api_key)
    # Batch embed: call embed_content per text to keep ordering simple and predictable.
    vectors: List[List[float]] = []
    for t in texts:
        resp = genai.embed_content(model=GEMINI_MODEL, content=t)
        vectors.append(resp["embedding"])  # type: ignore[index]
    return vectors


def embed_texts(texts: List[str]) -> List[List[float]]:
    if PROVIDER == "gemini":
        return _embed_gemini(texts)
    # default: openai
    return _embed_openai(texts)
