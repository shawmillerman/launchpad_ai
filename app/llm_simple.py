"""
Simple LLM wrapper for OpenAI only (Phase 1).

No provider abstraction yet—we ship with OpenAI.
Gemini support can be added when a user requests it.
"""

import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


def get_api_key():
    """Streamlit secret first, then environment variable."""
    try:
        import streamlit as st
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    return os.getenv("OPENAI_API_KEY")


def get_openai_chat(model: str = "gpt-4o-mini", temperature: float = 0.7):
    """Create OpenAI chat model for recipe coaching."""
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found in environment or Streamlit secrets")
    return ChatOpenAI(model=model, temperature=temperature, openai_api_key=api_key)


def get_openai_embeddings(model: str = "text-embedding-3-small"):
    """Create OpenAI embeddings for recipe retrieval."""
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found in environment or Streamlit secrets")
    return OpenAIEmbeddings(model=model, openai_api_key=api_key)
