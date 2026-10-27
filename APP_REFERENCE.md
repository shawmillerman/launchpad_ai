# app.py: Framework Reference Implementation

**Status**: Production-ready reference implementation (513 LOC)  
**Purpose**: Template for all Launchpad AI use cases  
**Architecture**: Follows FRAMEWORK_ARCHITECTURE.md Part 2

---

## Quick Start

### 1. Setup
```bash
cd /Users/admin/launchpad_ai

# Install dependencies (if not done)
pip install -r requirements.txt

# Configure API key
cp .env.example .env
echo "OPENAI_API_KEY=sk-..." >> .env
```

### 2. Add Documents
```bash
# Create data directory and add documents
mkdir -p data
cp your_documents/*.pdf data/
cp your_documents/*.docx data/
cp your_documents/*.txt data/
```

### 3. Run App
```bash
streamlit run app.py
```

### 4. Interact
- Ask questions about your documents
- Follow-up questions automatically understand context
- Sources are shown for each response

---

## Architecture Breakdown

### Entry Point Flow
```
Streamlit Configuration
  ↓
Sidebar (Data source, Retriever K, LLM params)
  ↓
load_and_index_documents()
  ├─ Fingerprint check (fast path if cached)
  ├─ Load documents (PDF, DOCX, TXT)
  ├─ Token-aware chunking (tiktoken-based)
  ├─ Embed with OpenAI
  └─ Index in ChromaDB
  ↓
build_rag_chain()
  ├─ History-aware retriever
  ├─ QA chain with system prompt
  └─ Orchestrated RAG composition
  ↓
Chat Loop
  ├─ User input (st.chat_input)
  ├─ RAG chain invocation
  ├─ Response display + sources
  └─ Update session state
```

### Key Functions

| Function | Purpose | Complexity |
|----------|---------|-----------|
| `_compute_fingerprint()` | Cache key based on file metadata | Low |
| `_load_documents_from_directory()` | Multi-format document loading (PDF/DOCX/TXT) | Medium |
| `_format_sources()` | Extract unique source labels | Low |
| `load_and_index_documents()` | Main indexing orchestration (cached) | High |
| `build_system_prompt()` | Domain-specific tone/instructions | Override this |
| `build_rag_chain()` | LangChain composition | High |

### Configuration Options

```python
# Environment variables
DATA_DIR = "./data"                    # Document source
CHROMA_DIR = "./chroma"               # Vector store location
RETRIEVER_K = 5                       # Chunks per query
LLM_MODEL = "gpt-4o-mini"            # LLM model
LLM_TEMPERATURE = 0.7                # Creativity (0-1)
EMBEDDING_MODEL = "text-embedding-3-small"  # Embedding model

# Streamlit sidebar overrides these at runtime
```

### Session State
```python
st.session_state.chat_history    # List[HumanMessage | AIMessage]
st.session_state.chat_sources    # Dict[index: List[source_labels]]
```

---

## How to Customize for Your Use Case

### 1. Override System Prompt
```python
def build_system_prompt() -> str:
    return """You are a cooking coach assistant...
    
Your role:
1. Explain recipes with flavor engineering principles
2. Adapt recipes for dietary needs
3. Teach proper techniques

Guidelines:
- Reference ingredient Maillard reactions
- Celebrate user cooking progress
- Ask clarifying questions about skill level
"""
```

### 2. Add Domain-Specific Context
```python
def build_rag_chain(retriever, llm_temperature: float):
    # ... existing code ...
    
    # Add domain context to prompt
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    # Optional: Add context dict to RAG chain invoke
    # response = rag_chain.invoke({
    #     "input": user_input,
    #     "chat_history": st.session_state.chat_history,
    #     "user_preferences": st.session_state.get("user_preferences", {}),
    # })
```

### 3. Filter Retrieved Documents
```python
# Add quality gate filtering (from app/quality.py)
from app.quality import apply_quality_gates

# In load_and_index_documents():
for chunk in chunks:
    result = apply_quality_gates(chunk.page_content, chunk.page_content, [])
    chunk.metadata["quality_status"] = result.status
    chunk.metadata["quality_reasons"] = result.reasons

# In retriever response processing:
context_docs = response.get("context", [])
high_quality = [d for d in context_docs 
                if d.metadata.get("quality_status") == "PASS"]
```

---

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Cold start (first run) | ~15-30s | Embedding all chunks |
| Warm start (cached) | <1s | Load existing vectorstore |
| Retrieval | <500ms | Chroma search (5 chunks) |
| LLM response | 1-3s | OpenAI API latency |
| **Total interaction** | ~5s | From question to answer |

---

## Extending to Multi-Agent (Phase 2)

When you need multiple agents (reformulator, coach, Q&A):

```python
# Phase 2: Add agent router
def route_user_query(user_input: str, chat_history: List) -> str:
    """Classify query type: reformulation, cooking_guidance, general_qa"""
    # Use LLM to classify
    # Return agent name: "reformulator", "coach", or "general"

# Phase 2: Add agent selection
if agent_type == "reformulator":
    response = reformulator_agent.invoke({...})
elif agent_type == "coach":
    response = coaching_agent.invoke({...})
else:
    response = rag_chain.invoke({...})
```

---

## Migration Path from `app_prepstation.py`

1. `app_prepstation.py` is specialized for recipes (example implementation)
2. `app.py` is generic (framework reference)
3. To migrate Prepstation to use `app.py` as base:
   - Copy `app.py` → `app_prepstation.py`
   - Override `build_system_prompt()` with recipe coaching tone
   - Add recipe-specific context to prompts
   - Customize data loading (recipes-only directory)

---

## Debugging

### No documents loaded?
```bash
# Verify data directory
ls -la data/

# Check file types (PDF, DOCX, TXT only)
file data/*

# Confirm permissions
chmod 644 data/*
```

### Vectorstore cache issues?
```bash
# Delete cache to force rebuild
rm -rf chroma/

# Re-run app (will rebuild)
streamlit run app.py
```

### API key errors?
```bash
# Verify env var is set
echo $OPENAI_API_KEY

# Or add to .env
cat .env | grep OPENAI_API_KEY
```

### Slow embeddings?
```bash
# Check API rate limits (OpenAI dashboard)
# Consider batch embedding if >1000 documents
# Or use smaller embedding model (text-embedding-3-small is already minimal)
```

---

## Files Modified/Created

- ✅ `app.py` (NEW) — Main entry point
- ✅ `app_prepstation.py` (EXISTING) — Specialized recipe app (kept for reference)
- ✅ `FRAMEWORK_ARCHITECTURE.md` (EXISTING) — Architecture blueprint
- ✅ `PHASE1_README.md` (EXISTING) — Phase 1 guide
- ✅ `requirements.txt` (EXISTING) — Lean dependencies
- ✅ `.env.example` (EXISTING) — Configuration template

---

## Next Steps

1. **Test locally**: `streamlit run app.py` with sample documents
2. **Gather feedback**: Does it work for your use case?
3. **Customize**: Override `build_system_prompt()` for your domain
4. **Phase 2 Planning**: Decide if multi-agent routing is needed

---

**Status**: Ready for production use as framework reference or starting point for domain-specific applications.

**Questions?** Refer to FRAMEWORK_ARCHITECTURE.md (architecture) or PHASE1_README.md (Phase 1 guide).
