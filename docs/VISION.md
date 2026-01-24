# Launchpad AI - Vision

**Build once, launch many.**

## The Problem

Every AI application starts by rebuilding the same infrastructure:
- Text extraction from PDFs and documents
- Chunking and embedding text
- Vector similarity search
- Quality validation (is this text garbage?)
- Citation and source tracking
- Learning from expert feedback

This is expensive, time-consuming, and error-prone. We rebuild these systems for every new idea.

## The Solution

**Launchpad AI is a product-agnostic AI engine** that provides battle-tested infrastructure for rapid application development.

Clone it. Configure it. Launch your idea.

## Core Philosophy

### 1. Configuration Over Code
Behavior is driven by YAML/JSON files, not hardcoded logic. Change the config, not the codebase.

**Example**: Want stricter quality gates? Edit `config/quality_gates.yaml`. Done.

### 2. Transparency & Auditability
Every AI decision includes:
- Source citations
- Confidence scores
- Reasoning trace
- Metadata for debugging

Students, users, and auditors can understand *why* the AI made a decision.

### 3. Expert Calibration
AI improves by learning from expert examples:
- Capture expert decisions (grades, feedback, classifications)
- Store as calibration examples with embeddings
- Use similarity search to find relevant examples for new inputs
- Adapt over time as more expert data accumulates

### 4. Quality First
Garbage in = Garbage out. Validate everything:
- Word count thresholds
- Text extraction quality
- Retention ratios (how much boilerplate was removed?)
- Format validation

Catch problems *before* expensive LLM calls.

### 5. Multi-Provider by Default
Don't lock into one LLM provider:
- OpenAI for embeddings
- Gemini for generation
- Local Ollama for privacy-sensitive tasks

Plug-and-play architecture.

## Design Principles (from Project Blackboard)

Launchpad AI inherits proven patterns from production systems:

| Principle | What It Means |
|-----------|---------------|
| **Transparent** | Every decision has citations and audit trails |
| **Consistent** | Same rules applied every time (no AI drift) |
| **Auditable** | Log inputs, outputs, and reasoning at every stage |
| **Human-Centered** | AI assists; humans decide |
| **Pedagogically Grounded** | Ground in actual documents, not generic knowledge |

## What Makes This Different

**Not a chatbot framework** - We provide the infrastructure layer below chatbots.

**Not application-specific** - No recipe logic, grading rules, or domain assumptions.

**Not a toy** - Production-grade patterns from systems processing thousands of documents.

**Not opinionated about LLMs** - Swap providers via config.

## Use Cases

### Assessment Systems
Ground grading in rubrics and calibration examples (Project Blackboard model).

### Course Chatbots
Answer student questions from official course materials (Clean IQ model).

### Recipe Assistants
Extract recipes from images, reformulate for dietary needs, guide cooking (Step Chef).

### Document Intelligence
Extract insights from enterprise documents with quality validation.

### Learning from Experts
Capture expert decisions and use them to guide future AI outputs.

## Success Metrics

Launchpad AI succeeds when:
1. **Time to MVP**: New application goes from idea → working prototype in days, not weeks
2. **Code Reuse**: 80%+ of infrastructure code comes from Launchpad AI
3. **Quality**: Applications built on Launchpad have transparent, auditable outputs
4. **Flexibility**: Easy to swap LLM providers or adjust behavior via config

## Non-Goals

- **Not a full application**: You still build your UI, business logic, and integrations
- **Not production DevOps**: You handle Docker, K8s, monitoring, etc.
- **Not domain-specific**: Recipe reformulation logic belongs in Step Chef, not here

## Roadmap Phases

### Phase 1: Core Infrastructure (4 weeks)
- Text ingestion (PDF, DOCX, TXT)
- Multi-provider embedding
- Vector retrieval
- Quality gates
- Configuration system

### Phase 2: Calibration Engine (3 weeks)
- Expert example capture
- Similarity-based calibration retrieval
- Temporal decay
- Component-based scoring

### Phase 3: Advanced Features (ongoing)
- Progressive rigor (phase-aware adaptation)
- Rubric-as-code patterns
- Citation generation
- Confidence scoring

### Phase 4: Example Applications
- Step Chef (recipe assistant)
- Clean IQ v2 (course chatbot)
- [Your idea here]

## Getting Started

1. Clone Launchpad AI
2. Review `docs/ROADMAP.md` for implementation plan
3. Check `docs/ARCHITECTURE.md` for technical design
4. Build your application layer on top

---

**Launchpad AI: Your AI infrastructure, ready to launch.**
