# Launchpad AI Phase 1: Lean & Complete

**Status**: Phase 1 Complete ✅  
**Deployment**: Streamlit app ready to run  
**Use Case**: Prepstation (AI Cooking Assistant)

---

## What Changed (vs. Legacy Multi-Agent Framework)

### ❌ Removed (Bloat)
- FastAPI/Uvicorn (no server yet—Streamlit is the UI)
- FAISS + naive retrieval dual implementation (using Chroma only)
- Provider abstraction (hardcoded OpenAI for Phase 1)
- Image/OCR ingestion (defer until user requests)
- Quality gates on ingest (apply on retrieval instead)
- Calibration loop scaffolding (build when we have user data)
- Config management (not needed for MVP)

### ✅ Kept & Simplified
- **Document ingestion** (PDF, DOCX, TXT via LangChain loaders)
- **Token-aware chunking** (better than character splitting)
- **Chroma vectorstore** (persistent, simple, reliable)
- **LangChain RAG composition** (create_retrieval_chain pattern from Socratica)
- **Streamlit session state** (simple, free memory management)
- **OpenAI embeddings** (fast, reliable)

### 🆕 Added
- **Prepstation app** (`app_prepstation.py`)
- **Example recipes** (3 detailed recipes to demo the flow)
- **Simplified LLM wrapper** (`app/llm_simple.py`)
- **Simple ingestion** (`app/ingest_simple.py`)
- **Lean dependencies** (10 packages, down from 16)

---

## Architecture (Phase 1)

```
User Input
    ↓
[Streamlit UI] ← Session State (chat history)
    ↓
[Load Recipes] → [Chunk] → [Embed] → [Chroma Vectorstore]
    ↓
[Retriever] (k=5 most similar recipes)
    ↓
[LangChain RAG Chain] (history-aware, context-aware)
    ├─ History-Aware Retriever (reformulates questions based on chat context)
    ├─ Question-Answer Chain (LLM + system prompt + retrieved context)
    ↓
[LLM Response] (gpt-4o-mini, temp=0.7)
    ↓
[Display + Sources] → User sees answer + retrieved recipe names
```

**Key Difference from Legacy**: Everything flows end-to-end in one direction. No branching logic, no multi-agent complexity, no deferred decisions. Build something that works, ship it, then expand.

---

## How to Run

### 1. Clone & Setup
```bash
cd /Users/admin/launchpad_ai

# Create venv (or use existing)
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
# Copy env template
cp .env.example .env

# Add your OpenAI API key
echo "OPENAI_API_KEY=sk-..." >> .env
```

### 3. Run the App
```bash
streamlit run app_prepstation.py
```

The app will:
1. Load recipes from `data/recipes/`
2. Embed them with OpenAI embeddings
3. Cache in `chroma_prepstation/` (skipped on subsequent runs)
4. Launch browser at `http://localhost:8501`

### 4. Try Demo Interactions
- **Ask about a recipe**: "What's in Spaghetti Carbonara?"
- **Request reformulation**: "Make the beef stew spicier"
- **Get cooking guidance**: "What do I do if my sauce breaks?"
- **Learn technique**: "Why is searing important?"

---

## Project Structure

```
launchpad_ai/
├── app_prepstation.py          # Main Streamlit app (Phase 1)
├── app/
│   ├── chunking.py             # Token-aware splitting (keep as-is)
│   ├── llm_simple.py           # OpenAI wrapper (no provider abstraction)
│   ├── ingest_simple.py        # Document loading (PDF/DOCX/TXT)
│   ├── quality.py              # Quality gates (kept, not used yet)
│   ├── embed.py                # OLD provider abstraction (DELETE in Phase 2)
│   ├── ingest.py               # OLD complex ingestion (DELETE in Phase 2)
│   └── ... (other old modules to deprecate)
├── data/
│   └── recipes/
│       ├── carbonara.txt       # Example: Spaghetti Carbonara
│       ├── beef_stew.txt       # Example: French Beef Stew
│       └── chicken_stirfry.txt # Example: Quick Stir-Fry
├── chroma_prepstation/         # Vectorstore cache (auto-created)
├── requirements.txt            # Lean dependencies (Phase 1)
├── .env.example               # Config template
└── README.md                  # This file
```

---

## Example Recipes Included

### 1. Spaghetti Carbonara (Classic Roman)
Teaches emulsion technique, fat rendering, and proper timing. Demonstrates why technique matters more than ingredients.

**Prepstation questions you could ask:**
- "How do I prevent scrambling the eggs?"
- "Can I use pancetta instead of guanciale?"
- "Make this version spicier"
- "Simplify this for beginners"

### 2. Beef Stew (French Beef Bourguignon Style)
Teaches Maillard reaction, fond development, and multi-step flavor building. Shows how searing and slow cooking create depth.

**Prepstation questions you could ask:**
- "What's the difference between searing and braising?"
- "Why does this take 3 hours?"
- "Make this easier/faster"
- "What wine should I use?"

### 3. Chicken Stir-Fry (Flavor-Optimized for Speed)
Teaches heat management, timing optimization, and parallel prep. Shows how to build flavor in 15 minutes.

**Prepstation questions you could ask:**
- "How do I prevent soggy vegetables?"
- "Can I prep everything in advance?"
- "Make this vegetarian"
- "What's the time-optimization trick here?"

---

## Key Design Decisions (Phase 1)

### 1. Streamlit (not FastAPI)
**Why**: Immediate interactive experience. No server plumbing, no API design decisions. Users see results instantly.  
**When to revisit**: Phase 2+ if we need a mobile app or integration with other services.

### 2. Chroma (not FAISS)
**Why**: Simpler mental model, persistent by default, built-in vector operations.  
**When to revisit**: Phase 3 if performance becomes an issue (Chroma is fine for ~10k recipes).

### 3. OpenAI Only (no provider abstraction)
**Why**: Ship now, add Gemini when someone asks. Abstractions before you need them are complexity tax.  
**When to revisit**: Phase 2 if competitive pressure requires Gemini support.

### 4. LangChain RAG (not custom chains)
**Why**: Proven pattern from Socratica, handles history + context + retrieval seamlessly.  
**When to revisit**: Never—this is core and it works.

### 5. Simple .txt recipes (not database)
**Why**: Easy to version control, easy to edit, human-readable, no schema overhead.  
**When to revisit**: Phase 2 when we have 100+ recipes and want richer metadata.

---

## What's NOT in Phase 1 (Defer to Phase 2+)

❌ **Multi-Agent Orchestration**: Single agent (the LLM) that answers questions. Add multi-agent routing when we have 3+ agents.

❌ **Calibration Loop**: We don't have user feedback data yet. Build this when users start rating recipes.

❌ **Image/OCR**: Users will initially upload text or PDF. OCR is a nice-to-have, not a blocker.

❌ **Voice Interface**: Hands-free cooking is Phase 3+. UI is stable on text first.

❌ **Configuration**: Everything is hardcoded or env-var simple. Config management is premature.

❌ **Real-time Timers**: Multi-timer management is Phase 2 (low complexity, high UX value).

---

## Performance Notes

- **Cold start** (first run): ~10 seconds (embedding + Chroma creation)
- **Warm start** (subsequent runs): <1 second (cached vectorstore)
- **Retrieval**: <500ms (5 most similar recipes)
- **LLM response**: 1-3 seconds (depends on answer length)
- **Full user interaction**: ~5 seconds (from question to answer)

For Phase 1 MVP with 3-5 recipes, this is plenty fast. Chroma scales to 10k+ documents before optimization is needed.

---

## Testing the App Locally

```bash
# Open another terminal
streamlit run app_prepstation.py

# In the Streamlit UI:
1. Select a recipe (sidebar should show "3 recipes loaded")
2. Ask a question: "What's Carbonara?"
3. Request reformulation: "Make it vegetarian"
4. Get guidance: "Why is Maillard important?"

# Each response should include:
- Answer from LLM
- Expandable "Sources" section with recipe names
- Proper formatting and Prepstation tone
```

---

## Next Steps

### Phase 2 (Multi-Agent Routing)
Add agents for specific tasks:
- **Recipe Reformulator Agent**: Flavor engineering, dietary adaptations
- **Cooking Coach Agent**: Real-time guidance, troubleshooting
- **Nutrition Agent**: Calorie counts, dietary info

### Phase 3 (Calibration Loop)
- Capture user ratings
- Store as calibration examples
- Use similarity search for personalized suggestions

### Phase 4 (Voice & Real-time)
- Voice input/output
- Multi-timer management
- Proactive health checks during cooking

---

## Troubleshooting

### App doesn't start
```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Check API key
echo $OPENAI_API_KEY  # Should be set
```

### No recipes found
```bash
# Verify data directory
ls -la data/recipes/

# Should see: carbonara.txt, beef_stew.txt, chicken_stirfry.txt
```

### Chroma cache issues
```bash
# Delete and rebuild cache
rm -rf chroma_prepstation/

# Re-run app (will rebuild)
streamlit run app_prepstation.py
```

---

## Files to Delete in Phase 2

Once we confirm Phase 1 works:
- `app/embed.py` (provider abstraction, replaced by llm_simple.py)
- `app/ingest.py` (old complex ingestion, replaced by ingest_simple.py)
- `app/ingest_image.py` (image/OCR, defer to Phase 2)
- `app/ingest_text_file.py` (unnecessary, handled by ingest_simple.py)
- `app/docx_reader.py` (unnecessary, LangChain's Docx2txtLoader is fine)
- `app/retrieval.py` (old naive retrieval, using Chroma)
- `app/vector_store.py` (old FAISS wrapper, using Chroma)
- `pyproject.toml` (not used for Phase 1 Streamlit app)
- `docs/` (legacy design docs, will update post-MVP)

---

## Questions for Future

1. **Should we add web UI instead of Streamlit?** (Probably Phase 3+, when mobile is needed)
2. **When do we need multi-agent routing?** (When a single agent can't handle all scenarios)
3. **Should recipes live in a database?** (When we have 100+ recipes and rich metadata)
4. **Do we need real-time collaboration?** (Multiple users cooking same recipe simultaneously—Phase 4+)

---

**Status**: Phase 1 complete and ready for user feedback. Ship this, learn from users, then expand deliberately.
