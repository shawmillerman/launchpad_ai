# Launchpad AI - Implementation Roadmap

**Version**: 1.0  
**Date**: January 24, 2026  
**Status**: Planning Phase

---

## Quick Timeline

| Phase | Duration | Estimated Completion | Status |
|-------|----------|----------------------|--------|
| **Phase 0** (Foundation) | 1 day | ✅ Jan 24 | Complete |
| **Phase 1** (Ingestion) | 1 week | Jan 31 | Next |
| **Phase 2** (Embeddings) | 1 week | Feb 7 | Planned |
| **Phase 3** (Retrieval) | 1 week | Feb 14 | Planned |
| **Phase 4** (Calibration) | 2 weeks | Feb 28 | Planned |
| **GitHub Publish** | 1-2 hrs | Feb 28 | After Phase 4 |

**Total**: ~5 weeks to production-ready engine

**Parallel work**: Step Chef MVP can begin after Phase 3 (Feb 14), allowing overlap with Phase 4.

**Lean path for Step Chef (1 week)**: Build only what Step Chef needs—PDF/TXT+OCR ingest, single-provider OpenAI embeddings, minimal FAISS retrieval, light config/env, basic logging. Skip multi-provider abstractions, calibration, and full schema validation until after MVP.

**Assumptions**: Full-time solo dev, 40 hrs/week. Adjust timeline proportionally for part-time work.

---

## Overview

This roadmap tracks the phased implementation of Launchpad AI as a product-agnostic infrastructure layer for AI applications.

**Goal**: Provide battle-tested, reusable components that reduce time-to-MVP for AI applications from weeks to days.

---

## Phase 0: Foundation & Documentation ✅

**Timeline**: 1 day (completed)  
**Status**: ✅ Complete

### Completed
- [x] Project structure (clean_iq model)
- [x] Core documentation (README, VISION, ROADMAP)
- [x] Architecture design document
- [x] Example application concepts (Step Chef)
- [x] Requirements baseline

### Deliverables
- Project structure matches clean_iq pattern
- Documentation provides clear vision and roadmap
- Ready for implementation

---

## Phase 1: Core Ingestion Pipeline

**Timeline**: 1 week  
**Priority**: Critical  
**Status**: 🔄 Next

### Objectives
Build the text processing pipeline with quality validation.

### Tasks

#### 1.1 Document Ingestion
- [ ] PDF text extraction (pdfplumber or pypdf)
- [ ] DOCX extraction (python-docx, preserve structure)
- [ ] TXT file reading with encoding detection
- [ ] Batch processing support
- [ ] Error handling and logging

**Code**: `app/ingest.py`

#### 1.2 Text Chunking
- [ ] Token-based chunking (tiktoken)
- [ ] Configurable chunk size and overlap
- [ ] Paragraph boundary preservation
- [ ] Metadata tracking (source file, chunk index)

**Code**: `app/chunking.py`

#### 1.3 Quality Gates
- [ ] Word count validation
- [ ] Retention ratio calculation (text vs boilerplate)
- [ ] Format validation
- [ ] Quality status flags (OK_FOR_PROCESSING, NEEDS_REVIEW, REJECTED)
- [ ] Configurable thresholds

**Code**: `app/quality.py`

#### 1.4 Configuration System
- [ ] YAML/JSON config loading
- [ ] Schema validation
- [ ] Default configs
- [ ] Config override via environment variables

**Code**: `app/config.py`  
**Config**: `config/ingest.yaml`, `config/quality_gates.yaml`

### Success Criteria
- Ingest 100 mixed documents (PDF, DOCX, TXT)
- Quality gates flag <5% false positives
- Clean text extraction with structure preserved
- All behavior driven by config files

### Dependencies
None (foundational phase)

---

## Phase 2: Multi-Provider Embeddings

**Timeline**: 1 week  
**Priority**: Critical  
**Status**: 🔄 Planned

### Objectives
Build plug-and-play embedding infrastructure supporting multiple LLM providers.

### Tasks

#### 2.1 Embedding Interface
- [ ] Abstract `Embedder` base class
- [ ] Common interface: `embed(texts: List[str]) -> List[List[float]]`
- [ ] Batch processing support
- [ ] Error handling and retries

**Code**: `app/embed.py`

#### 2.2 Provider Implementations
- [ ] **OpenAI**: text-embedding-3-small, text-embedding-3-large
- [ ] **Google Gemini**: embedding-001 (priority for next build)
- [ ] **Anthropic**: Voyage embeddings (future)
- [ ] **Local**: Ollama support (future)

**Code**: `app/providers/openai.py`, `app/providers/gemini.py`

#### 2.3 Provider Selection
- [ ] Config-driven provider selection
- [ ] Environment variable support
- [ ] Fallback providers
- [ ] Cost tracking per provider

**Config**: `config/embedding.yaml`

#### 2.4 Caching & Optimization
- [ ] Embedding cache (avoid re-embedding same text)
- [ ] Batch size optimization
- [ ] Rate limiting
- [ ] Cost estimation

### Success Criteria
- Switch between OpenAI and Gemini via config change only
- Embed 1000 chunks with caching (95%+ cache hit rate on reruns)
- Sub-second response for cached embeddings
- Clear cost tracking

### Dependencies
Phase 1 complete (need chunked text to embed)

---

## Phase 3: Vector Retrieval System

**Timeline**: 1 week  
**Priority**: Critical  
**Status**: 🔄 Planned

### Objectives
Build semantic search with metadata filtering and citation tracking.

### Tasks

#### 3.1 Vector Store
- [ ] FAISS index management
- [ ] Add/update/delete operations
- [ ] Metadata storage (JSONL sidecar)
- [ ] Index persistence and loading

**Code**: `app/vector_store.py`

#### 3.2 Retrieval Engine
- [ ] Similarity search (cosine distance)
- [ ] Top-k retrieval
- [ ] Metadata filtering (source, category, date)
- [ ] Distance thresholds
- [ ] Re-ranking (optional)

**Code**: `app/retrieval.py`

#### 3.3 Citation Generation
- [ ] Source attribution for each result
- [ ] Citation format templates
- [ ] Deduplication
- [ ] Confidence scoring

**Code**: `app/citations.py`

#### 3.4 Fallback Strategies
- [ ] Handle empty results gracefully
- [ ] Expand search radius if insufficient results
- [ ] Log retrieval quality metrics

### Success Criteria
- Retrieve relevant chunks with <100ms latency
- Metadata filtering works correctly
- Citations trace back to original documents
- Handles 10K+ document corpus

### Dependencies
Phase 2 complete (need embeddings for vector search)

---

## Phase 4: Calibration Engine

**Timeline**: 2 weeks  
**Priority**: High  
**Status**: 🔄 Planned

### Objectives
Enable learning from expert examples over time.

### Tasks

#### 4.1 Calibration Capture
- [ ] Expert decision schema (input, output, feedback, metadata)
- [ ] Storage format (JSONL or SQLite)
- [ ] Timestamping and versioning
- [ ] Tagging and categorization

**Code**: `app/calibration/capture.py`

#### 4.2 Calibration Retrieval
- [ ] Similarity search over calibration examples
- [ ] Metadata filtering (week, phase, category)
- [ ] Fallback strategies (specific → general)
- [ ] Distance-based confidence

**Code**: `app/calibration/retrieval.py`

#### 4.3 Temporal Decay
- [ ] Exponential decay for old examples
- [ ] Configurable decay rate
- [ ] Preserve critical examples (flagged by expert)

**Code**: `app/calibration/decay.py`

#### 4.4 Score Range Computation
- [ ] Compute ranges from calibration data (IQR method)
- [ ] Confidence intervals
- [ ] Component-based scoring support
- [ ] Outlier detection

**Code**: `app/calibration/scoring.py`

### Success Criteria
- Capture 100 expert examples
- Retrieve relevant examples with <80% similarity
- Decay reduces old example weight over time
- Score ranges tighten with more data

### Dependencies
Phase 3 complete (need retrieval for calibration search)

---

## Phase 5: Advanced Features

**Timeline**: Ongoing  
**Priority**: Medium  
**Status**: 🔄 Backlog

### Progressive Rigor
- [ ] Phase-aware adaptation (early/mid/late term)
- [ ] Dynamic threshold adjustment
- [ ] Confidence progression modeling

### Rubric-as-Code
- [ ] Hierarchical rubric storage
- [ ] Version control for rubrics
- [ ] Rubric-to-scoring logic mapping

### Component Scoring
- [ ] Multi-dimensional assessment
- [ ] Per-component feedback generation
- [ ] Component range computation

### LLM Generation (Optional)
- [ ] Multi-provider LLM wrappers (not just embeddings)
- [ ] Prompt template management
- [ ] Response parsing and validation

---

## Example Applications

### Step Chef (Recipe Assistant)

**Timeline**: 1-2 weeks after Phase 3  
**Status**: Concept phase

See: `docs/applications/STEPCHEF.md`

**What it demonstrates:**
- Recipe text extraction (PDF/image OCR)
- Recipe reformulation (flavor profiles, dietary restrictions)
- Step-by-step guidance with calibration
- Real-time cooking alerts

**Infrastructure from Launchpad AI:**
- Text ingestion (recipe extraction)
- Embedding & retrieval (similar recipes)
- Quality gates (valid recipe structure)
- Calibration (learn from user preferences)

**Step Chef-specific code:**
- Recipe parsing logic
- Flavor reformulation algorithms
- Cooking timer integration
- UI/UX for cooking guidance

---

## Technical Debt & Refactoring

### Known Issues
- None yet (greenfield project)

### Future Refactors
- [ ] Database abstraction (support PostgreSQL, not just FAISS)
- [ ] Async processing for large batches
- [ ] Distributed embedding generation
- [ ] API rate limiting and quotas

---

## Decision Log

### Decision 1: Use clean_iq as Template
**Date**: 2026-01-24  
**Rationale**: clean_iq has proven structure (app/, docs/, data/, artifacts/). Reuse rather than rebuild.

### Decision 2: Multi-Provider Embeddings
**Date**: 2026-01-24  
**Rationale**: Don't lock into OpenAI. Gemini and Anthropic offer competitive performance and pricing.

### Decision 3: Configuration-Driven Behavior
**Date**: 2026-01-24  
**Rationale**: Learned from Project Blackboard that hardcoded rules are maintenance nightmares. Config files enable rapid iteration.

### Decision 4: Quality Gates First
**Date**: 2026-01-24  
**Rationale**: Garbage in = Garbage out. Validate before expensive LLM calls.

---

## Success Metrics

### Developer Experience
- **Time to MVP**: <1 week from clone to working prototype
- **Code Reuse**: 80%+ of infrastructure from Launchpad AI
- **Configuration Changes**: Behavior changes via config, not code

### System Quality
- **Retrieval Accuracy**: 90%+ relevant results in top-5
- **Embedding Cache Hit Rate**: 95%+ on repeated runs
- **Quality Gate Precision**: <5% false positives

### Production Readiness
- **Documentation Coverage**: 100% of public APIs
- **Test Coverage**: 80%+ for core modules
- **Error Handling**: Graceful degradation, never crash

---

## Next Steps

1. **Immediate (15 minutes)**:
   - ✅ Complete documentation (this file)
   - ✅ Capture Step Chef concept
   - ✅ Create TODO checklist

2. **Next Session (1-2 hours)**:
   - Implement Phase 1: Ingestion pipeline
   - Build quality gates
   - Test with sample documents

3. **Week 1-2**:
   - Complete Phases 1-3 (ingestion → embeddings → retrieval)
   - Test end-to-end with real documents

4. **Week 3-4**:
   - Implement calibration engine (Phase 4)
   - Build example application (Step Chef or Clean IQ v2)

---

**Last Updated**: 2026-01-24  
**Next Review**: After Phase 1 completion
