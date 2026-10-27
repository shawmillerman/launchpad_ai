# Launchpad AI & Socratica: Master Architecture Blueprint

**Version**: 1.0  
**Last Updated**: October 2026  
**Status**: Phase 1 Complete, Phase 2+ Planned  
**Maintainer**: Principal Architect

---

## Executive Summary

This document defines the unified architecture of **Launchpad AI** (rebuilt as a lean, modular framework) and its primary implementation **Prepstation** (AI Cooking Assistant). It distills lessons learned from three projects:

1. **Project Blackboard** — Early multi-agent prototype (suspended; archived for reference)
2. **Socratica** — Proven single-purpose RAG app (active production)
3. **Launchpad AI** — Rebuilt general-purpose framework combining best practices

**Core Principle**: Ship working software with focused scope, then expand deliberately based on user feedback—not speculative architecture.

---

## Part 1: Architectural Evolution & History

### Project Blackboard (2025, Suspended)
**Scope**: Educational AI grading system with multi-agent orchestration  
**Architecture**: Multiple specialized agents (essay grader, plagiarism detector, rubric validator) coordinated through a central router  
**Why It Stalled**:
- Over-engineered for MVP (started with infrastructure before product)
- Multi-agent routing added complexity without clear use cases
- Front-end integration became the bottleneck, not the AI backend
- Dependency overhead (FastAPI, FAISS, provider abstraction, image OCR)
- Configuration layer designed but not implemented
- Calibration loop scaffolded but untested

**Lessons Learned**:
- ❌ Don't build infrastructure before you have a working product
- ❌ Don't abstract for future needs you don't have yet
- ✅ Archive code (don't delete) for reference and historical context
- ✅ Focus on end-to-end flow first; optimize later

**Current Status**: Code archived on `archive-legacy-v1` branch for reference.

---

### Socratica (2025, Production Active)
**Scope**: Interactive AI tutor for PSU higher-ed courses  
**Architecture**: Single Streamlit entry point with direct session state  
**Why It Works**:
- 589 lines of `app.py` + 457 lines of utilities (lean codebase)
- No microservice complexity; no FastAPI/server plumbing
- Direct session state management via Streamlit's built-in system
- LangChain RAG composition (proven pattern for history-aware retrieval)
- Persistent ChromaDB indexed by course fingerprint (automatic invalidation on file change)
- Focus on domain logic (pedagogy, tone, course calendars) not infrastructure

**Key Techniques**:
1. **History-Aware Retriever**: Reformulates follow-up questions against chat context before retrieval
2. **Stuff Documents Chain**: Sends full retrieved context to LLM for synthesis
3. **Fingerprint-Based Caching**: Hash of file paths/mtimes/sizes triggers index rebuild on changes
4. **Session-Based State**: Streamlit handles all persistence; no external state backend needed

**Current Status**: Production-grade, deployed and active.

**Proof Point**: A single developer built, deployed, and maintains a production educational AI tool with minimal infrastructure.

---

### Launchpad AI (2025-2026, Rebuilt)

#### Original Vision (Pre-Rebuild)
A general-purpose framework supporting multiple use cases (grading, recipe coaching, etc.) with:
- Multi-provider LLM support (OpenAI, Gemini, Anthropic)
- Pluggable ingestion pipelines (PDF, DOCX, TXT, images with OCR)
- Quality gate validation (word count, retention ratio, extraction warnings)
- Calibration loop for expert-in-the-loop learning
- Configuration-as-code driving all behaviors
- FAISS vector search with metadata filtering

**What Happened**: 
- Modules were created for each abstraction
- No orchestration layer connected them
- No working application demonstrated the flow
- Complexity accumulated without delivering value
- When faced with building Prepstation, we had to choose: use the legacy framework or rebuild from first principles

#### Phase 1 Rebuild (October 2026)
**Decision**: Rebuild from scratch, using Socratica as the execution model template.

**What Changed**:
- ❌ Removed: FastAPI/Uvicorn (Streamlit is sufficient for MVP)
- ❌ Removed: Provider abstraction (hardcode OpenAI; add Gemini when requested)
- ❌ Removed: FAISS dual implementation (Chroma is simpler, persistent by default)
- ❌ Removed: Image/OCR support (defer to Phase 2; users have PDF alternatives)
- ❌ Removed: Configuration layer scaffolding (env vars + hardcoding works for MVP)
- ✅ Kept: Token-aware chunking (superior to character splitting)
- ✅ Kept: Hierarchical document structure preservation (DOCX headings)
- ✅ Kept: Quality gates module (repurposed for retrieval-time filtering)
- ✅ Adopted: Socratica's Streamlit + LangChain model

**Result**: A lean, working framework that can be expanded without fundamental redesign.

---

## Part 2: The New Master Framework Blueprint

### 2.1 Core Execution Model (From Socratica)

#### Single Entry Point
```
app_<use_case>.py  (e.g., app_prepstation.py, app_socratica.py)
├─ Streamlit UI
├─ Session state management
├─ Document loading & caching
├─ LangChain RAG chain assembly
└─ User interaction loop
```

**Why Streamlit, Not FastAPI?**
- MVP requirement: Interactive feedback loop with users (not batch API processing)
- No server plumbing: Reduces cognitive load, speeds deployment
- Built-in features: Session state, caching, UI components
- Trade-off: Not ideal for multi-client systems; add API layer in Phase 3+ if needed

#### Direct Session State
```python
st.session_state["chat_history"] = [HumanMessage(...), AIMessage(...), ...]
st.session_state["chat_sources"] = {message_index: [sources], ...}
```

**Why Not a Database?**
- MVP scope: Single-user, browser-based interaction
- Simplicity: No connection pools, schema migrations, or state reconciliation
- Persistence: Streamlit's session survives app reruns (browser session)
- Scale-up path: Phase 3+ can add persistent storage if multi-user is needed

#### Linear LangChain RAG Chain
```python
# 1. History-aware retriever reformulates questions
contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", "Given chat history and a question, reformulate it..."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

# 2. QA chain answers using retrieved context
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", build_system_prompt()),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

# 3. Compose into single RAG chain
rag_chain = create_retrieval_chain(
    history_aware_retriever,
    question_answer_chain
)

# 4. Invoke
response = rag_chain.invoke({
    "input": user_input,
    "chat_history": st.session_state["chat_history"],
    **context_dict  # Additional context (e.g., course calendar)
})
```

**Why This Pattern?**
- Proven in Socratica (production-tested)
- Handles follow-up questions naturally (history awareness)
- Modular: Easy to swap retriever or QA chain
- LangChain manages composition; we don't reinvent plumbing

#### Persistent Vector Store (ChromaDB)
```python
@st.cache_resource
def load_docs(path):
    # 1. Check if vectorstore exists
    persist_dir = f"./chroma/{fingerprint}"
    if os.path.isdir(persist_dir):
        return Chroma(persist_directory=persist_dir).as_retriever()
    
    # 2. Load documents
    documents = load_documents(path)
    chunks = text_splitter.split_documents(documents)
    
    # 3. Embed and index
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
    )
    return vectorstore.as_retriever()
```

**Why Chroma?**
- Persistent by default (auto-saves to disk)
- Simple to reason about (no FAISS configuration)
- Scales to 10k+ documents (sufficient for Phase 1-3)
- Fingerprint-based invalidation (automatic cache invalidation on file change)

---

### 2.2 Superior Ingestion & Chunking (From Launchpad AI)

#### Token-Aware Chunking
```python
def split_by_tokens(text: str, max_tokens: int = 500, overlap: int = 100):
    """Split by token count, not character count.
    
    Better for LLMs because:
    - Respects actual context window boundaries
    - Avoids mid-token splitting (tiktoken handles this)
    - Consistent chunk size in LLM terms
    """
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk = enc.decode(tokens[start:end])
        if chunk.strip():
            chunks.append(chunk.strip())
        if end == len(tokens):
            break
        start = end - overlap
    return chunks
```

**Advantage Over Character Splitting**:
- Socratica uses `RecursiveCharacterTextSplitter(chunk_size=1000)` (character-based)
- This can split mid-token or mid-word
- Token-aware splitting is more predictable for LLM context

**Usage**:
```python
# In ingestion
chunks = split_by_tokens(document_text, max_tokens=500, overlap=100)
```

#### Format-Based Document Loaders
```python
def load_documents_from_directory(path: str) -> List[Document]:
    """Load PDF, DOCX, TXT with format-specific handling."""
    documents = []
    
    # PDFs: Extract text per page
    pdf_loader = DirectoryLoader(path, glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents.extend(pdf_loader.load())
    
    # DOCX: Preserve heading structure
    # (read_docx_with_headings extracts both text and heading metadata)
    docx_loader = DirectoryLoader(path, glob="**/*.docx", loader_cls=Docx2txtLoader)
    documents.extend(docx_loader.load())
    
    # TXT: Plain text files
    txt_loader = DirectoryLoader(path, glob="**/*.txt", loader_cls=TextLoader)
    documents.extend(txt_loader.load())
    
    return documents
```

**Hierarchical Metadata Preservation**:
```python
# For DOCX files with structured headings:
# "Chapter 1: Introduction"
# "  Section 1.1: Foundations"
# "    Subsection 1.1.1: Core Concepts"

chunks = read_docx_with_headings(path)
# Returns: (text_chunks, [{"heading_1": "Introduction", "heading_2": "Foundations", ...}, ...])
```

**Why This Matters**:
- Retrieval can filter by heading hierarchy ("only show results from Chapter 1")
- LLM can understand document structure (e.g., "According to the Introduction section...")
- Better source attribution in chat (can say "Chapter 1, Section 1.1")

---

### 2.3 Quality Gates (Repurposed for Retrieval-Time Filtering)

#### Original Purpose (Launchpad AI)
Applied during ingestion to flag low-quality extracted text (OCR artifacts, boilerplate-heavy documents).

#### New Purpose (Phase 1+)
Applied during retrieval to ensure high-relevance chunks hit the prompt.

```python
def apply_quality_gates(
    raw_text: str,
    cleaned_text: str,
    extraction_warnings: List[str],
    min_word_count: int = 30,
    min_retention_ratio: float = 0.15,
) -> QualityResult:
    """Validate chunk quality."""
    reasons = []
    
    word_count = len(cleaned_text.split())
    retention_ratio = len(cleaned_text) / max(len(raw_text), 1)
    
    if word_count < min_word_count:
        reasons.append(f"low_word_count:{word_count}")
    if retention_ratio < min_retention_ratio:
        reasons.append(f"low_retention_ratio:{retention_ratio:.2f}")
    if extraction_warnings:
        reasons.extend(extraction_warnings)
    
    return QualityResult(
        status="PASS" if not reasons else "NEEDS_REVIEW",
        reasons=reasons,
        word_count=word_count,
        retention_ratio=retention_ratio,
    )
```

**When to Use**:
- Phase 2+: Apply during retrieval to filter low-quality chunks before they reach the LLM
- Phase 1: Stored in metadata but not enforced (MVP doesn't need filtering)

---

### 2.4 Module Responsibilities (Clear Division of Labor)

```
launchpad_ai/
├── app_<use_case>.py          # Entry point (Streamlit UI)
│                              # Responsibilities:
│                              # - Session state management
│                              # - Document loading & caching
│                              # - RAG chain assembly
│                              # - User interaction loop
│
├── app/
│   ├── llm_simple.py          # LLM interface (OpenAI only, Phase 1)
│   │                          # Responsibilities:
│   │                          # - get_openai_chat() → ChatOpenAI instance
│   │                          # - get_openai_embeddings() → OpenAIEmbeddings
│   │                          # - API key management (env vars + Streamlit secrets)
│   │
│   ├── ingest_simple.py       # Document loading (PDF, DOCX, TXT)
│   │                          # Responsibilities:
│   │                          # - load_documents_from_directory()
│   │                          # - load_single_document()
│   │                          # - Format-specific handling
│   │
│   ├── chunking.py            # Token-aware text splitting
│   │                          # Responsibilities:
│   │                          # - split_by_tokens() using tiktoken
│   │                          # - Consistent chunk sizing
│   │
│   ├── quality.py             # Quality validation
│   │                          # Responsibilities:
│   │                          # - apply_quality_gates()
│   │                          # - Word count, retention ratio validation
│   │                          # - Extraction warning handling
│   │
│   └── [DEPRECATED in Phase 2]
│       ├── embed.py           # Old provider abstraction (DELETE)
│       ├── ingest.py          # Old complex ingestion (DELETE)
│       ├── ingest_image.py    # Image/OCR (DELETE)
│       ├── vector_store.py    # Old FAISS wrapper (DELETE)
│       ├── retrieval.py       # Old naive search (DELETE)
│
└── data/
    └── recipes/               # Application-specific data (recipes, courses, etc.)
```

---

## Part 3: Design Principles

### 1. **Ship First, Abstract Later**
- **Principle**: Build working software for the specific use case before generalizing.
- **Lesson from Blackboard**: We over-abstracted (multi-provider, config layer, calibration loop) without a working app to drive decisions.
- **Lesson from Socratica**: Hardcoding is fine if it works; refactor when you have real requirements.
- **Application**: Phase 1 uses hardcoded OpenAI. Phase 2 adds Gemini support *if users ask for it*.

### 2. **Linear Execution > Microservice Complexity**
- **Principle**: Single-threaded, linear request-response flow until you prove you need parallelism.
- **Lesson from Blackboard**: Multi-agent routing seemed powerful in theory; in practice, we never built it.
- **Lesson from Socratica**: Single LLM + single RAG chain handles course tutoring perfectly.
- **Application**: Phase 1 is single-agent. Phase 2 adds agent routing *if the single agent can't handle all question types*.

### 3. **Session State > Persistent Backend (Until You Need Multi-User)**
- **Principle**: Use in-memory session state as long as sessions are per-user, per-browser.
- **Lesson from Socratica**: Streamlit's `st.session_state` eliminates entire categories of bugs (race conditions, state reconciliation).
- **Lesson from Blackboard**: We designed for distributed state without a concrete multi-user requirement.
- **Application**: Phase 1-2 use session state. Phase 3+ considers multi-user persistence *if that's the business requirement*.

### 4. **Fingerprint-Based Caching > Manual Invalidation**
- **Principle**: Hash source file metadata to auto-detect changes and invalidate caches.
- **Implementation**:
  ```python
  def _fingerprint(path):
      h = hashlib.sha1()
      for file in sorted(os.walk(path)):
          h.update(f"{file}|{size}|{mtime}".encode())
      return h.hexdigest()
  
  persist_dir = f"./chroma/{fingerprint}"
  # If files change, fingerprint changes, new persist_dir is used
  ```
- **Why**: No cache invalidation bugs; file changes automatically trigger rebuild.

### 5. **Focus on Domain Logic, Not Infrastructure**
- **Principle**: Let frameworks (Streamlit, LangChain, ChromaDB) handle plumbing; you write domain code.
- **Breakdown**:
  - Infrastructure: Session state, caching, HTTP routing, vector indexing
  - Domain Logic: Pedagogy (Socratica), flavor engineering (Prepstation), question understanding
- **Application**: Spend 80% of effort on domain, 20% on infrastructure.

### 6. **Defer Every "Someday" Feature**
- **Principle**: If it's not in the MVP spec, defer it. Seriously defer it.
- **Deferred (Good Decisions)**:
  - Image/OCR ingestion (users can upload PDFs)
  - Multi-agent routing (single agent handles MVP)
  - Calibration loop (need user feedback data first)
  - Voice interface (text-based works for MVP)
  - Web UI (Streamlit is the UI)
  - Nutritional analysis (feature creep)
- **Added (Bad Decisions)**:
  - Provider abstraction (Blackboard, before a use case required it)
  - Configuration layer (Blackboard, before we had config to manage)
  - FAISS + naive retrieval dual implementation (Blackboard, over-engineered for MVP)

---

## Part 4: Technology Stack & Rationale

### Core Stack (Phase 1)
| Component | Choice | Why | Alternative | Why Not |
|-----------|--------|-----|--------------|---------|
| **UI Framework** | Streamlit | Interactive, built-in components, no DevOps | FastAPI | Overkill for MVP |
| **LLM Chain** | LangChain | Proven RAG patterns, active community | LlamaIndex | Larger API surface |
| **Vector Store** | ChromaDB | Persistent by default, simple API | FAISS | Requires manual persistence |
| **Embeddings** | OpenAI | Reliable, good quality, established | Gemini | Add when users ask |
| **Document Loading** | LangChain loaders | Standardized, format-aware | Custom parsers | Reinventing wheels |
| **Chunking** | Tiktoken-based | Token-aware, respects context windows | Character-based | Less predictable |
| **Language** | Python 3.10+ | ML/AI standard, vast library ecosystem | JavaScript | Wrong domain |

### Deferred Technologies
- **FastAPI** — Add if/when we need a REST API (Phase 3+)
- **PostgreSQL** — Add if/when we need multi-user persistence (Phase 3+)
- **Redis** — Add if/when we need distributed caching (Phase 3+)
- **Docker** — Add when deployment infrastructure is defined (Phase 2+)
- **Kubernetes** — Add when scale demands it (Phase 4+, if ever)

---

## Part 5: Data Flow & Architecture Diagram

### Prepstation Phase 1 Data Flow
```
┌─────────────────────────────────────────────────────────────────┐
│ USER INTERACTION LOOP                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. User Input (Streamlit chat_input)                            │
│     ↓                                                              │
│  2. Append to st.session_state["chat_history"]                   │
│     ↓                                                              │
│  3. RAG Chain Invocation                                          │
│     ├─ history_aware_retriever                                   │
│     │  ├─ Contextualize question against chat history           │
│     │  ├─ Reformulate to standalone question                    │
│     │  └─ Search Chroma vectorstore (k=5)                        │
│     │                                                              │
│     └─ question_answer_chain                                     │
│        ├─ System prompt (Prepstation tone)                       │
│        ├─ Chat history                                           │
│        ├─ Retrieved recipe context                               │
│        ├─ User question                                          │
│        └─ LLM response synthesis                                 │
│     ↓                                                              │
│  4. Response display + sources                                   │
│     ├─ Answer text                                               │
│     ├─ Expandable "Sources" section                              │
│     └─ Retrieved recipe names                                    │
│     ↓                                                              │
│  5. Append to st.session_state (for next iteration)              │
│     ↓                                                              │
│  [Loop back to User Input]                                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ INITIALIZATION (Once per app session)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. Load recipes from data/recipes/                              │
│     ↓                                                              │
│  2. Compute fingerprint (SHA1 of file paths + mtimes)            │
│     ↓                                                              │
│  3. Check if vectorstore exists                                  │
│     ├─ YES: Load from chroma_prepstation/{fingerprint}/          │
│     └─ NO: Continue to ingestion                                 │
│     ↓                                                              │
│  4. Chunk recipes (split_by_tokens, max=500, overlap=100)        │
│     ↓                                                              │
│  5. Embed chunks (OpenAI text-embedding-3-small)                 │
│     ↓                                                              │
│  6. Index in Chroma (persist_directory = chroma_prepstation/...) │
│     ↓                                                              │
│  7. Return retriever (chroma.as_retriever(k=5))                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part 6: Module Interaction & Extension Points

### How Modules Communicate
```
app_prepstation.py
├─ Calls: load_recipes(RECIPES_DIR)
│  └─ Returns: Retriever (chroma_vectorstore.as_retriever)
│
├─ Calls: load_docs() → internally uses:
│  ├─ ingest_simple.load_documents_from_directory()
│  ├─ chunking.split_by_tokens()
│  └─ get_openai_embeddings()
│
├─ Builds RAG chain:
│  ├─ LangChain create_history_aware_retriever()
│  ├─ LangChain create_stuff_documents_chain()
│  └─ LangChain create_retrieval_chain()
│
└─ Invokes: rag_chain.invoke({input, chat_history, ...})
   └─ Calls: get_openai_chat() internally (LangChain)
```

### Extension Points (Where to Add Phase 2+ Features)

**1. Add Multi-Agent Routing**
```python
# Phase 2: Add to app_prepstation.py after RAG chain invocation
router_agent = route_question(user_input, chat_history)
# "reformulation" → reformulator_agent
# "cooking_guidance" → cooking_coach_agent
# "general_qa" → default_rag_chain
```

**2. Add Provider Abstraction**
```python
# Phase 2: Create app/llm.py (replaces llm_simple.py)
# Add provider switching logic:
if EMBED_PROVIDER == "gemini":
    embeddings = get_gemini_embeddings()
else:
    embeddings = get_openai_embeddings()
```

**3. Add Quality Gate Enforcement**
```python
# Phase 2: In retrieval step (before chunks hit LLM)
context_docs = retriever.invoke(reformulated_q)
quality_checked = [d for d in context_docs 
                   if apply_quality_gates(d.page_content).passed]
```

**4. Add Persistent User Profiles**
```python
# Phase 3: Add database storage for multi-user
# Track per-user state instead of session state
user_id = st.query_params.get("user_id")
chat_history = fetch_user_history(user_id)
# After each response:
persist_user_history(user_id, chat_history)
```

---

## Part 7: Scalability & Performance Characteristics

### Phase 1 Limits
| Dimension | Limit | Bottleneck | When to Optimize |
|-----------|-------|-----------|-----------------|
| **Recipes** | ~10 recipes (POC) | Embedding latency | 50+ recipes |
| **Chunk Count** | ~500 chunks | Chroma search latency | 5000+ chunks |
| **Concurrent Users** | 1 (per session) | Streamlit architecture | 10+ simultaneous |
| **Embedding Dimension** | 1536 (OpenAI) | Network latency | Custom embeddings needed |
| **Retrieval Speed** | <500ms | Chroma local search | Distributed Chroma |
| **LLM Latency** | 1-3s | OpenAI API response | Faster model or batching |

### Scaling Strategy
- **Phase 1-2** (POC): Session-based, single Chroma instance, local deployment
- **Phase 3** (Pilot): Persistent database, multi-user, Streamlit Cloud
- **Phase 4** (Scale): Distributed Chroma, API-first (FastAPI), load balancing

---

## Part 8: Known Limitations & Technical Debt

### Phase 1 Limitations (Intentional)
- 🟡 Single LangChain agent (no multi-agent routing yet)
- 🟡 Hardcoded OpenAI (no provider switching yet)
- 🟡 Session-based state only (no multi-user persistence)
- 🟡 No voice interface (text-only for MVP)
- 🟡 No image/OCR support (users upload PDFs)
- 🟡 Quality gates not enforced (stored in metadata only)

### Technical Debt (To Address in Phase 2+)
- 🔴 `app/embed.py` — Old provider abstraction (DELETE)
- 🔴 `app/ingest.py` — Old complex ingestion (DELETE)
- 🔴 `app/ingest_image.py` — Image/OCR handling (DELETE unless Phase 2 needs it)
- 🔴 `app/vector_store.py` — Old FAISS wrapper (DELETE)
- 🔴 `app/retrieval.py` — Old naive search (DELETE)
- 🟡 `pyproject.toml` — Not used by Streamlit (migrate to requirements.txt-only)
- 🟡 No tests for RAG chain (add pytest + fixtures in Phase 2)
- 🟡 No monitoring/logging (add in Phase 3 if production)

### Why Keep Legacy Code?
- Historical reference (understand what was tried and why)
- Code archaeology (future engineers can learn from mistakes)
- Explicit deletion (easier to deprecate deliberately than delete accidentally)

---

## Part 9: Decision Log

### Major Architectural Decisions

| Date | Decision | Rationale | Alternative | Trade-Off |
|------|----------|-----------|-------------|-----------|
| **Oct 2026** | Use Streamlit (not FastAPI) for MVP | Interactive feedback loop, built-in features, no DevOps | FastAPI + React | Can't serve multiple users simultaneously |
| **Oct 2026** | Hardcode OpenAI (not provider abstraction) | Ship now, add Gemini when users ask | Multi-provider from day 1 | Refactoring required if Gemini becomes required |
| **Oct 2026** | Single LangChain agent (not multi-agent router) | No use cases for agent specialization in MVP | Multi-agent from day 1 | Need Phase 2 if routing becomes necessary |
| **Oct 2026** | Session state only (not database) | Simplicity, no schema management | Multi-user from day 1 | Single-user only; add DB in Phase 3 |
| **Oct 2026** | ChromaDB (not FAISS) | Persistent by default, simpler API | FAISS | Scales to 10k docs; revisit if bigger |
| **Oct 2026** | Text recipes only (not OCR) | MVP scope, users can upload PDFs | Image/OCR support | Requires Phase 2 for image recipes |
| **Oct 2026** | Archive legacy code (not delete) | Preserve history, avoid "archaeology" later | Clean delete | Repository size (negligible for now) |

---

## Part 10: Phase Timeline & Roadmap

### Phase 1 ✅ (Complete, Oct 2026)
- [x] Streamlit entry point
- [x] Document loading (PDF, DOCX, TXT)
- [x] Token-aware chunking
- [x] ChromaDB vectorstore
- [x] LangChain RAG chain (history-aware)
- [x] Example recipes (3 detailed samples)
- [x] System prompt (Prepstation tone)
- [x] Chat history management

**Deliverables**: Working app, ready for user feedback

---

### Phase 2 (Planned, Nov-Dec 2026)
- [ ] Multi-agent routing
  - [ ] Reformulator agent (flavor engineering, dietary adaptations)
  - [ ] Cooking coach agent (real-time guidance, troubleshooting)
  - [ ] Router logic (question classification)
- [ ] Quality gate enforcement (retrieval-time filtering)
- [ ] User testing (5-10 beta users)
- [ ] Feedback loop (iterate based on learnings)
- [ ] Unit tests (pytest + fixtures for RAG chain)
- [ ] Delete legacy modules

**Key Question**: Do we actually need multi-agent routing, or does a single capable agent suffice?

---

### Phase 3 (Planned, Jan-Mar 2027)
- [ ] Calibration loop
  - [ ] Capture user ratings
  - [ ] Store as calibration examples
  - [ ] Similarity-based personalization
- [ ] Persistent multi-user backend
  - [ ] PostgreSQL for user profiles
  - [ ] Streamlit Cloud deployment
- [ ] Real-time multi-timer management
- [ ] Advanced flavor engineering
- [ ] Monitoring & logging

---

### Phase 4+ (Future, TBD)
- [ ] Voice interface (hands-free coaching)
- [ ] Image/OCR support (recipe photos)
- [ ] Web UI (if Streamlit proves limiting)
- [ ] API-first architecture (if B2B integrations needed)
- [ ] Distributed system (if global scale required)

---

## Part 11: How to Use This Document

### For Developers
- **Starting a new feature**: Read Section 2 (execution model) to align with patterns
- **Adding a new module**: Use Section 2.4 (module responsibilities) as a template
- **Making architectural decisions**: Consult Section 3 (design principles)
- **Extending the framework**: Refer to Section 6 (extension points)

### For Product Managers
- **Scoping features**: Check the roadmap (Part 10) and deferred features (Part 3.3)
- **Understanding trade-offs**: Read Section 7 (scalability) and Section 9 (decision log)
- **Prioritizing next work**: Phase 2 needs user feedback to decide on multi-agent routing

### For Architects
- **System design reviews**: Use Section 5 (data flow) and Section 4 (stack rationale)
- **Scaling planning**: Consult Section 7 (performance limits)
- **Technical debt management**: Reference Section 8 (known limitations)

### For Historians
- **Understanding why decisions were made**: Read Part 1 (evolution) and Part 9 (decision log)
- **Avoiding past mistakes**: Study what was deferred (Part 3.3) and why

---

## Conclusion

**Launchpad AI Phase 1** is a deliberate reset from the over-engineered Blackboard framework. It adopts Socratica's proven execution model (single entry point, direct session state, linear RAG chains) while incorporating Launchpad's superior ingestion and chunking techniques.

The result is a lean, working system that can be extended deliberately based on real user feedback—not speculative architecture.

**Next milestone**: Gather user feedback on Phase 1, then decide whether Phase 2 requires multi-agent routing or if a single capable agent is sufficient.

---

**Document Status**: Living document. Update when major decisions are made or phases complete.  
**Last Updated**: October 27, 2026  
**Maintained By**: Principal Architect  
**Next Review**: Post-Phase 1 user feedback (November 2026)
