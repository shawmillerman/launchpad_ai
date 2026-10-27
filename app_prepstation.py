"""
Prepstation: AI Cooking Assistant
Phase 1: Lean, end-to-end Streamlit + LangChain + ChromaDB RAG app

Execution model copied from Socratica:
1. Load recipes from data/recipes/
2. Embed with OpenAI embeddings
3. Cache in Chroma vectorstore
4. Retrieve context + LLM chain for Q&A and reformulation
5. Simple Streamlit UI for interaction
"""

import os
import sys
import hashlib
import shutil
from pathlib import Path
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document

# Import simplified utilities
from app.chunking import split_by_tokens
from app.llm_simple import get_openai_chat, get_openai_embeddings

load_dotenv()

# Configuration
RECIPES_DIR = "./data/recipes"
CHROMA_DIR = "./chroma_prepstation"
RETRIEVER_K = 5
INDEX_VERSION = "1"


def _recipe_fingerprint(path: str) -> str:
    """Hash of recipe file paths, sizes, mtimes (plus INDEX_VERSION) to detect changes."""
    h = hashlib.sha1(INDEX_VERSION.encode())
    recipe_path = Path(path)
    if recipe_path.exists():
        for file in sorted(recipe_path.glob("**/*")):
            if file.is_file():
                stat = file.stat()
                h.update(f"{file}|{stat.st_size}|{int(stat.st_mtime)}".encode())
    return h.hexdigest()[:10]


def _load_recipes_from_directory(path: str) -> list[Document]:
    """Load all .txt recipe files from a directory into Document objects."""
    documents = []
    recipe_path = Path(path)

    if not recipe_path.exists():
        return documents

    for recipe_file in sorted(recipe_path.glob("*.txt")):
        try:
            with open(recipe_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                documents.append(
                    Document(
                        page_content=content,
                        metadata={
                            "source": str(recipe_file),
                            "recipe_name": recipe_file.stem,
                        },
                    )
                )
        except Exception as e:
            st.warning(f"Failed to read {recipe_file}: {e}")

    return documents


@st.cache_resource
def load_recipes(recipes_dir: str):
    """Load recipes, embed, and cache in Chroma vectorstore."""
    if not Path(recipes_dir).exists():
        return None

    collection_name = "recipes"
    fingerprint = _recipe_fingerprint(recipes_dir)
    persist_dir = os.path.join(CHROMA_DIR, f"{collection_name}_{fingerprint}")
    embeddings = get_openai_embeddings()

    # If cache exists, reuse it
    if os.path.isdir(persist_dir):
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_dir,
        )
        return vectorstore.as_retriever(search_kwargs={"k": RETRIEVER_K})

    # Otherwise, load and index recipes
    documents = _load_recipes_from_directory(recipes_dir)
    if not documents:
        return None

    # Token-aware chunking (better for LLM context)
    chunks = []
    for doc in documents:
        text_chunks = split_by_tokens(doc.page_content, max_tokens=500, overlap=100)
        for chunk in text_chunks:
            chunks.append(
                Document(
                    page_content=chunk,
                    metadata={"source": doc.metadata["source"],
                             "recipe_name": doc.metadata["recipe_name"]},
                )
            )

    # Embed and store
    try:
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=collection_name,
            persist_directory=persist_dir,
        )
    except Exception:
        shutil.rmtree(persist_dir, ignore_errors=True)
        raise

    return vectorstore.as_retriever(search_kwargs={"k": RETRIEVER_K})


def _build_system_prompt():
    """System prompt for recipe coaching and reformulation."""
    return """You are Prepstation, an AI cooking assistant that transforms recipes through flavor engineering and personalization.

Your role:
1. **Understand recipes** at a technical level (techniques, flavor profiles, timing)
2. **Reformulate recipes** with actual cooking knowledge (sear for Maillard, bloom spices, deglaze for fond)
3. **Adapt for preferences** (spicy, simple, dietary needs, skill level)
4. **Explain the why** (why this technique matters, what happens chemically)
5. **Coach interactively** (answer questions mid-cooking, offer substitutions, troubleshoot)

Your tone:
- **Inspirational**: Celebrate techniques ("You're building flavor on a molecular level")
- **Clear**: Explain what you're doing and why
- **Empowering**: Make users feel like capable cooks ("I know you're a baller chef")
- **Practical**: Give concrete actions, not just theory

When responding:
- If asked to reformulate: Show the original and modified recipe with explanations
- If asked during cooking: Give quick, actionable advice
- If asked about technique: Explain not just how, but why it works
- If adapting for dietary needs: Maintain flavor and satisfaction, not just swap ingredients"""


# Streamlit UI
st.set_page_config(page_title="Prepstation | AI Cooking Assistant", layout="wide")

st.title("🍳 Prepstation")
st.caption("AI Cooking Assistant — Flavor Engineering & Interactive Guidance")

# Sidebar
with st.sidebar:
    st.title("Prepstation")
    st.caption("Your AI Cooking Coach")

    # Check if recipes are available
    if Path(RECIPES_DIR).exists():
        recipe_count = len(list(Path(RECIPES_DIR).glob("*.txt")))
        st.info(f"📚 {recipe_count} recipes loaded")
    else:
        st.warning("Add .txt recipe files to `data/recipes/` to get started")

    st.markdown("---")
    st.subheader("How to use")
    st.markdown("""
    1. **Upload recipes** (paste or save .txt files to `data/recipes/`)
    2. **Ask questions** about recipes or cooking
    3. **Request reformulations** (spicy, simplified, vegan, etc.)
    4. **Get interactive guidance** for step-by-step cooking
    """)

# Load recipes
retriever = load_recipes(RECIPES_DIR)

if retriever is not None:
    llm = get_openai_chat()

    # RAG Chain Setup
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", _build_system_prompt()),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "chat_sources" not in st.session_state:
        st.session_state["chat_sources"] = {}

    # Display chat history
    for i, message in enumerate(st.session_state["chat_history"]):
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.write(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.write(message.content)
                if st.session_state["chat_sources"].get(i):
                    with st.expander("📖 Sources"):
                        for source in st.session_state["chat_sources"][i]:
                            st.markdown(f"- {source}")

    # User input
    if user_input := st.chat_input("Ask about recipes, request a reformulation, or get cooking tips..."):
        with st.chat_message("user"):
            st.write(user_input)

        with st.spinner("🤔 Thinking..."):
            response = rag_chain.invoke({
                "input": user_input,
                "chat_history": st.session_state["chat_history"],
            })

        # Extract sources
        sources = []
        for doc in response.get("context", []):
            recipe_name = doc.metadata.get("recipe_name", "Unknown")
            if recipe_name not in sources:
                sources.append(recipe_name)

        answer = response["answer"].strip()

        # Update state
        st.session_state["chat_history"].append(HumanMessage(content=user_input))
        st.session_state["chat_history"].append(AIMessage(content=answer))
        msg_index = len(st.session_state["chat_history"]) - 1
        if sources:
            st.session_state["chat_sources"][msg_index] = sources

        st.rerun()

else:
    st.warning(
        "📁 No recipes found. Add .txt recipe files to `data/recipes/` to get started.\n\n"
        "Example recipe format:\n"
        "```\n"
        "Spaghetti Carbonara\n\n"
        "Ingredients:\n"
        "- 400g spaghetti\n"
        "- 200g guanciale (or pancetta)\n"
        "- 4 egg yolks\n"
        "- 100g Pecorino Romano\n\n"
        "Steps:\n"
        "1. Cut guanciale into 1/4-inch cubes...\n"
        "```"
    )
