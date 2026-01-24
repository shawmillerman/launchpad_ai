# Launchpad AI

**A product-agnostic AI engine for rapid application development.**

Launchpad AI provides the foundational infrastructure to build AI-powered applications. Clone this repo, configure it for your use case, and launch.

## Purpose

Build once, launch many. Launchpad AI extracts the reusable patterns from production AI applications (like Project Blackboard's assessment engine and Clean IQ's course chatbot) into a general-purpose toolkit.

## What it provides

### Core Infrastructure
- **Text Processing**: Ingest PDFs, DOCX, TXT with quality validation
- **Embedding & Retrieval**: Vector search with multiple provider support (OpenAI, Gemini, Anthropic)
- **Calibration Engine**: Learn from expert examples over time
- **Configuration System**: YAML/JSON-driven behavior (no hardcoded rules)
- **Quality Gates**: Validation before processing (garbage-in detection)
- **Citation & Traceability**: Every AI output links to its sources

### Design Principles (from Project Blackboard)
- **Transparent**: Every decision is auditable with citations
- **Configuration-as-Code**: Behavior driven by config files, not buried in code
- **Calibration Loop**: System learns from expert feedback
- **Structured Output**: Component-based responses, not opaque results
- **Quality First**: Validate input quality before processing
- **Progressive Refinement**: Adapt over time with more data

## Quick Start

```bash
# Clone and setup
git clone <your-repo>
cd launchpad_ai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add your API keys (OPENAI_API_KEY, GEMINI_API_KEY, etc.)

# Ingest documents
python -m app.ingest

# Run server
uvicorn app.server:create_app --factory --reload
```

## Project Structure

```
launchpad_ai/
├── app/                    # Core application code
│   ├── ingest.py          # Document ingestion (PDF, DOCX, TXT)
│   ├── retrieval.py       # Vector similarity search
│   ├── embed.py           # Multi-provider embedding wrapper
│   ├── calibration.py     # Expert example learning
│   ├── quality.py         # Quality gates & validation
│   ├── config.py          # Configuration management
│   └── server.py          # FastAPI server (optional)
├── data/                  # Input documents (gitignored)
├── artifacts/             # Vector stores, indexes (gitignored)
├── runs/                  # Processing runs (gitignored)
├── docs/                  # Project documentation
│   ├── VISION.md         # Project vision & philosophy
│   ├── ROADMAP.md        # Implementation roadmap
│   └── ARCHITECTURE.md   # Technical architecture
├── scripts/               # Helper scripts
├── tests/                 # Test suite
└── requirements.txt       # Python dependencies
```

## Example Applications

### Step Chef (Recipe Assistant)
Status: Concept phase  
An AI cooking assistant that reformulates recipes, guides step-by-step, and provides real-time cooking alerts.

See: [docs/applications/STEPCHEF.md](docs/applications/STEPCHEF.md)

### Your Next Idea
Launchpad AI provides:
- Text extraction and cleaning
- Semantic search over your documents
- Expert calibration (learn from your feedback)
- Multi-LLM support (switch between OpenAI, Gemini, Anthropic)
- Quality validation built-in

## How to Build an App with Launchpad AI

1. Place your app repo alongside this one (e.g., launchpad_ai/ and step_chef/ as sibling folders).
2. In your app repo, install Launchpad AI in editable mode:
  ```bash
  pip install -e ../launchpad_ai
  ```
3. Copy config templates as needed:
  - [.env.example](.env.example) → .env
  - Future config files under config/
4. Use Launchpad AI pipelines:
  - Ingest docs via [app/ingest.py](app/ingest.py) (once implemented)
  - Embed via [app/embed.py](app/embed.py) with provider chosen in .env
  - Retrieve via [app/retrieval.py](app/retrieval.py) (vector search with metadata)
5. Keep your domain logic in your app (e.g., recipe parsing in step_chef/app/); keep generic infra in Launchpad AI.

## LLM Provider Support

Launchpad AI includes plug-and-play LLM wrappers:

```python
from app.embed import get_embedder

# Switch providers via config
embedder = get_embedder("openai")  # or "gemini", "anthropic"
embeddings = embedder.embed(["your text"])
```

Supported providers:
- ✅ OpenAI (GPT-4, text-embedding-3-small)
- ✅ Google Gemini (coming soon)
- 🔄 Anthropic Claude (planned)
- 🔄 Local models via Ollama (planned)

## Configuration Philosophy

All behavior is configuration-driven:

```yaml
# config/voice.yaml
tone: professional
must_include:
  - citations
  - confidence_level
never:
  - make_assumptions
  - generate_without_sources
```

```yaml
# config/quality_gates.yaml
min_word_count: 30
min_retention_ratio: 0.15
require_citations: true
```

Change the config, not the code.

## Development Status

- ✅ Project structure established
- ✅ Documentation framework
- 🔄 Core ingestion pipeline (in progress)
- 🔄 Multi-provider embedding support (in progress)
- 🔄 Calibration engine (planned)
- 🔄 Quality gates (planned)

See `docs/ROADMAP.md` for detailed implementation plan.

## Not in Scope (for base engine)

- Application-specific UI/UX
- LMS/CRM integrations
- Analytics dashboards
- Production deployment configs (Docker, K8s, etc.)

These belong in your application layer that uses Launchpad AI.

## License

Private repository. Add license if publishing.

## Next Steps

1. Review `docs/VISION.md` for project philosophy
2. See `docs/ROADMAP.md` for implementation plan
3. Check `docs/ARCHITECTURE.md` for technical details
4. Explore `docs/applications/` for use case examples
