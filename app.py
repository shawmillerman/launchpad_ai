"""
Launchpad AI Framework - Main Entry Point
Phase 1: Lean, End-to-End Streamlit + LangChain RAG Application

This application demonstrates the unified architecture:
- Document loading (PDF, DOCX, TXT)
- Token-aware chunking
- ChromaDB persistent vector indexing
- LangChain history-aware RAG chain
- Streamlit interactive UI with session-based memory

Usage:
    streamlit run app.py

Environment:
    OPENAI_API_KEY: Your OpenAI API key
    DATA_DIR: Directory containing documents (default: ./data)
    CHROMA_DIR: Vector store directory (default: ./chroma)
"""

import os
import re
import sys
import hashlib
import shutil
from pathlib import Path
from typing import List, Optional

import streamlit as st
from dotenv import load_dotenv

from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Import custom modules
from app.chunking import split_by_tokens
from app.quality import apply_quality_gates

load_dotenv()

# ============================================================================
# Configuration
# ============================================================================

# Paths
DATA_DIR = os.getenv("DATA_DIR", "./data")
CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma")

# Vector store
RETRIEVER_K = int(os.getenv("RETRIEVER_K", "5"))
INDEX_VERSION = "2"  # Bump when ingestion/chunking changes

# LLM
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


# ============================================================================
# Utilities
# ============================================================================

def _get_api_key() -> str:
    """Retrieve OpenAI API key from Streamlit secrets or environment."""
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except (FileNotFoundError, KeyError):
        pass

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not found. Set it via environment variable or "
            "Streamlit secrets (secrets.toml)."
        )
    return api_key


def _compute_fingerprint(path: str, version: str = INDEX_VERSION) -> str:
    """
    Compute SHA1 hash of file paths, sizes, and mtimes.
    Changes to source files trigger vectorstore rebuild.
    """
    h = hashlib.sha1(version.encode())
    base_path = Path(path)

    if not base_path.exists():
        return h.hexdigest()[:10]

    for root, _dirs, files in sorted(os.walk(base_path)):
        for filename in sorted(files):
            filepath = os.path.join(root, filename)
            try:
                stat = os.stat(filepath)
                h.update(f"{filepath}|{stat.st_size}|{int(stat.st_mtime)}".encode())
            except OSError:
                pass

    return h.hexdigest()[:10]


def _load_documents_from_directory(path: str) -> List[Document]:
    """
    Load documents from directory supporting multiple formats:
    - PDF (via PyPDFLoader)
    - DOCX (via Docx2txtLoader)
    - TXT (via TextLoader)

    Returns:
        List of Document objects with content and metadata
    """
    documents = []

    if not Path(path).exists():
        return documents

    # Load PDFs
    try:
        pdf_loader = DirectoryLoader(
            path,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            recursive=True,
            show_progress=False,
        )
        documents.extend(pdf_loader.load())
    except Exception as e:
        st.warning(f"Warning: Failed to load PDFs: {e}")

    # Load DOCX
    try:
        docx_loader = DirectoryLoader(
            path,
            glob="**/*.docx",
            loader_cls=Docx2txtLoader,
            recursive=True,
            show_progress=False,
        )
        documents.extend(docx_loader.load())
    except Exception as e:
        st.warning(f"Warning: Failed to load DOCX files: {e}")

    # Load TXT
    try:
        txt_loader = DirectoryLoader(
            path,
            glob="**/*.txt",
            loader_cls=TextLoader,
            recursive=True,
            show_progress=False,
        )
        documents.extend(txt_loader.load())
    except Exception as e:
        st.warning(f"Warning: Failed to load TXT files: {e}")

    return documents


def _format_sources(docs: List[Document]) -> List[str]:
    """Extract unique, ordered source labels from retrieved documents."""
    seen = []
    for doc in docs:
        label = doc.metadata.get("source", "unknown")
        if label not in seen:
            seen.append(label)
    return seen


# ============================================================================
# Streamlit Configuration
# ============================================================================

st.set_page_config(
    page_title="Launchpad AI Engine",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚀 Launchpad AI Engine")
st.caption("Lean, End-to-End Document Retrieval & Reasoning")


# ============================================================================
# Sidebar Configuration
# ============================================================================

with st.sidebar:
    st.header("Configuration")

    # Data directory selection
    st.subheader("Data Source")
    data_dir_input = st.text_input(
        "Data Directory",
        value=DATA_DIR,
        help="Directory containing PDF, DOCX, or TXT files",
    )

    # Retriever parameters
    st.subheader("Retrieval")
    retriever_k = st.slider(
        "Context Chunks (k)",
        min_value=1,
        max_value=20,
        value=RETRIEVER_K,
        help="Number of most similar documents to retrieve",
    )

    # LLM parameters
    st.subheader("Language Model")
    llm_temp = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=LLM_TEMPERATURE,
        step=0.1,
        help="Model creativity (0=deterministic, 1=random)",
    )

    # System info
    st.subheader("System Status")
    data_path = Path(data_dir_input)
    if data_path.exists():
        doc_count = len(list(data_path.glob("**/*.pdf"))) + \
                   len(list(data_path.glob("**/*.docx"))) + \
                   len(list(data_path.glob("**/*.txt")))
        st.metric("Documents Found", doc_count)
    else:
        st.warning(f"Data directory not found: {data_dir_input}")

    # Help
    st.markdown("---")
    st.subheader("Help")
    st.markdown("""
    **How to use:**
    1. Add PDF, DOCX, or TXT files to your data directory
    2. Ask questions about your documents
    3. Follow-up questions understand context automatically
    4. Retrieved sources shown below each response

    **Tips:**
    - Use consistent file naming for better organization
    - Include metadata in document titles (e.g., "2026-Q1-Report.pdf")
    - Streamlit caches vectorstore by file fingerprint (auto-rebuild on changes)
    """)


# ============================================================================
# Document Loading & Vectorstore Initialization
# ============================================================================

@st.cache_resource
def load_and_index_documents(data_path: str, k: int) -> Optional[object]:
    """
    Load documents, chunk, embed, and index in ChromaDB.
    Cached by @st.cache_resource to persist across reruns.

    Args:
        data_path: Directory containing documents
        k: Number of chunks to retrieve

    Returns:
        Chroma retriever or None if no documents found
    """
    if not Path(data_path).exists():
        return None

    # Fingerprint-based cache invalidation
    fingerprint = _compute_fingerprint(data_path)
    collection_name = "documents"
    persist_dir = os.path.join(CHROMA_DIR, f"{collection_name}_{fingerprint}")

    # Initialize embeddings
    api_key = _get_api_key()
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, openai_api_key=api_key)

    # Check if vectorstore already exists
    if os.path.isdir(persist_dir):
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_dir,
        )
        return vectorstore.as_retriever(search_kwargs={"k": k})

    # Load documents
    with st.spinner("📂 Loading documents..."):
        documents = _load_documents_from_directory(data_path)

    if not documents:
        st.warning(f"No documents found in {data_path}")
        return None

    st.info(f"📚 Loaded {len(documents)} documents")

    # Token-aware chunking (superior to character-based splitting)
    with st.spinner("✂️ Chunking documents..."):
        chunks = []
        for doc in documents:
            text_chunks = split_by_tokens(
                doc.page_content,
                max_tokens=500,
                overlap=100
            )
            for chunk_text in text_chunks:
                chunks.append(
                    Document(
                        page_content=chunk_text,
                        metadata=doc.metadata,
                    )
                )

    st.info(f"📦 Created {len(chunks)} chunks")

    # Optional: Apply quality gates (for later, not enforced in Phase 1)
    # quality_results = []
    # for chunk in chunks:
    #     result = apply_quality_gates(chunk.page_content, chunk.page_content, [])
    #     quality_results.append(result)

    # Embed and index
    with st.spinner("🔢 Embedding and indexing..."):
        try:
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                collection_name=collection_name,
                persist_directory=persist_dir,
            )
        except Exception as e:
            st.error(f"Failed to create vectorstore: {e}")
            shutil.rmtree(persist_dir, ignore_errors=True)
            raise

    st.success("✅ Vectorstore ready")
    return vectorstore.as_retriever(search_kwargs={"k": k})


# ============================================================================
# LLM & RAG Chain Initialization
# ============================================================================

def build_system_prompt() -> str:
    """
    Build system prompt for the RAG chain.
    Override this in subclasses for domain-specific behavior.
    """
    return """You are a helpful AI assistant that answers questions based on provided documents.

Your role:
1. Answer questions using the retrieved document context
2. Cite sources when relevant
3. Acknowledge when you don't have enough information
4. Maintain a helpful, clear tone

Guidelines:
- Always ground your answer in the provided context
- If context doesn't address the question, say so explicitly
- Provide page numbers or section names when available
- Ask clarifying questions if the question is ambiguous
- Keep responses concise and well-organized"""


def build_rag_chain(retriever, llm_temperature: float):
    """
    Build LangChain RAG chain with history awareness.

    Architecture:
    1. History-aware retriever: Reformulates questions based on chat context
    2. QA chain: Synthesizes answer from context + history + current question
    3. RAG chain: Orchestrates retriever + QA chain
    """
    api_key = _get_api_key()
    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=llm_temperature,
        openai_api_key=api_key,
    )

    # Step 1: Contextualize question (handles "follow-up question" problem)
    contextualize_q_system_prompt = """Given a chat history and a question which might reference context in the chat history, \
formulate a standalone question which can be understood without the chat history. \
Do NOT answer the question, just reformulate it if needed and otherwise return it as is."""

    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    history_aware_retriever = create_history_aware_retriever(
        llm,
        retriever,
        contextualize_q_prompt,
    )

    # Step 2: Answer question (handles "confusing context" problem)
    qa_system_prompt = build_system_prompt()
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "Context:\n{context}\n\nQuestion: {input}"),
    ])

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # Step 3: Combine into RAG chain
    rag_chain = create_retrieval_chain(
        history_aware_retriever,
        question_answer_chain,
    )

    return rag_chain


# ============================================================================
# Main Application Loop
# ============================================================================

# Load and index documents
retriever = load_and_index_documents(data_dir_input, retriever_k)

if retriever is None:
    st.error(
        "❌ No documents loaded. Please ensure your data directory "
        f"({data_dir_input}) contains PDF, DOCX, or TXT files."
    )
    st.stop()

# Initialize RAG chain
rag_chain = build_rag_chain(retriever, llm_temp)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chat_sources" not in st.session_state:
    st.session_state.chat_sources = {}

# ============================================================================
# Chat Display Loop
# ============================================================================

st.subheader("Conversation")

# Display chat history
for i, message in enumerate(st.session_state.chat_history):
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.write(message.content)
            # Show sources if available
            if st.session_state.chat_sources.get(i):
                with st.expander("📖 Sources"):
                    for source in st.session_state.chat_sources[i]:
                        st.markdown(f"- `{source}`")

# ============================================================================
# User Input & Response Loop
# ============================================================================

if user_input := st.chat_input("Ask a question about your documents..."):
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)

    # Generate response
    with st.spinner("🤔 Thinking..."):
        try:
            response = rag_chain.invoke({
                "input": user_input,
                "chat_history": st.session_state.chat_history,
            })
        except Exception as e:
            st.error(f"Error generating response: {e}")
            st.stop()

    # Extract answer and sources
    answer = response.get("answer", "").strip()
    context_docs = response.get("context", [])
    sources = _format_sources(context_docs)

    # Display assistant response
    with st.chat_message("assistant"):
        st.write(answer)
        if sources:
            with st.expander("📖 Sources"):
                for source in sources:
                    st.markdown(f"- `{source}`")

    # Update session state
    st.session_state.chat_history.append(HumanMessage(content=user_input))
    st.session_state.chat_history.append(AIMessage(content=answer))
    msg_index = len(st.session_state.chat_history) - 1
    if sources:
        st.session_state.chat_sources[msg_index] = sources

    # Rerun to display new messages in the history loop
    st.rerun()
