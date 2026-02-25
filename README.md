<div align="center">

# Clarus

**Maximum-accuracy RAG search engine for sacred texts**

Comparative theological analysis across the Quran and Bible with multi-agent LLM synthesis,
morphological keyword search, multi-query semantic retrieval with RRF fusion, and full TR/EN localization.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&style=flat-square)](https://github.com/pre-commit/pre-commit)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776ab.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000.svg?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-DC382D.svg?style=flat-square&logo=qdrant&logoColor=white)](https://qdrant.tech)
[![Redis](https://img.shields.io/badge/Redis-DC382D.svg?style=flat-square&logo=redis&logoColor=white)](https://redis.io)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6.svg?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Sponsor](https://img.shields.io/badge/Sponsor-Polar.sh-6366F1.svg?style=flat-square)](https://polar.sh/claruss)

[✨ Features](#-features) · [🏗️ Architecture](#-architecture) · [📦 Collections](#-collections) · [🚀 Quick Start](#-quick-start) · [📖 Usage](#-usage) · [📡 API Reference](#-api-reference) · [🛠️ Tech Stack](#-tech-stack) · [📊 Performance](#-performance) · [🧪 Testing](#-testing) · [🤝 Contributing](#-contributing)

</div>

---

![Hub Dashboard](docs/screenshots/readme-hub.png)

---

## Overview

Clarus is a production-grade RAG system engineered for **maximum retrieval accuracy** on religious texts. It indexes ~123,000 verse vectors across 13 collections (8 Quran translations + Bible OT/NT/Apocrypha in English and Turkish), then uses multi-query semantic search with Reciprocal Rank Fusion to surface the most relevant passages before handing them to a 5-agent LLM pipeline for comparative theological synthesis.

The system is built for researchers, developers, and anyone who wants scholarly-quality cross-textual analysis without the noise of naive keyword search.

### ✦ Key Highlights

- **Multi-Query Semantic Search** — Dense embeddings (text-embedding-3-large, 3072-dim) with 3-5 LLM-generated query variants fused via RRF (k=60) for recall that no single query achieves alone
- **Multi-Agent Synthesis** — 5 specialized agents (Quran, OT, NT, Apocrypha, Summary) run in parallel and converge into a structured comparative essay with inline citations
- **Morphological Keyword Search** — Arabic root extraction across 1,651 roots and 77,429 words; Hebrew/Greek Strong's concordance for OT and NT
- **Confidence Scoring** — Two-phase sigmoid-calibrated scoring (Platt scaling) replacing naive weighted averages for calibrated retrieval confidence
- **Semantic Chunking** — Embedding-based verse grouping that preserves scriptural boundaries rather than splitting on arbitrary token counts
- **Production Infrastructure** — Better Auth, Redis semantic caching (60-80% cost reduction), SSE streaming, circuit breakers, Sentry observability
- **Full i18n** — Complete TR/EN localization with next-intl, Accept-Language detection, and locale-aware LLM response caching
- **13 Collections** — ~123,000 indexed vectors across 8 Quran translations + Bible OT/NT/Apocrypha in EN+TR

---

## ✨ Features

### Search & Retrieval

| Feature | Description |
|---------|-------------|
| **Semantic Search** | Dense embeddings (3072-dim, text-embedding-3-large) for context-aware verse retrieval across all 13 collections |
| **Multi-Query Search** | 3-5 LLM-generated query variants searched in parallel and fused via RRF for higher recall than single-query |
| **Semantic Chunking** | Groups semantically related verses preserving scriptural boundaries; separate implementations for Quran and Bible |
| **Multi-Query RAG** | 3-5 LLM-generated query variants per request, all fused via RRF for maximum recall |
| **Query Enhancement** | Gemini 2.5 Flash expands queries with synonyms, related concepts, and cross-language terms |
| **RRF Fusion** | Reciprocal Rank Fusion (k=60) merges multi-query results into a single ranked list |
| **Semantic Cache** | Redis-backed embedding similarity cache; 60-80% reduction in OpenAI API costs |
| **Multilingual Queries** | Query in 8 languages (TR, EN, ES, FR, IT, PT, AR, DE) with automatic detection and translation |

### Multi-Agent Comparative Analysis

```
Query → [QuranAgent, OTAgent, NTAgent, ApocryphaAgent] → SummaryAgent → Essay
```

Each agent searches its own collection independently, generates a focused commentary, and passes its findings to the Summary agent. The Summary agent synthesizes all four perspectives into a structured 5-paragraph essay with inline citations. Agents run in parallel via `asyncio.gather` to keep latency manageable.

| Agent | Collection | Role |
|-------|------------|------|
| QuranAgent | `quran_tr_*` | Quranic perspective and commentary (Turkish) |
| OldTestamentAgent | `bible_ot` | Torah, Prophets, and Writings (KJVA) |
| NewTestamentAgent | `bible_nt` | Gospels and Epistles (KJVA) |
| ApocryphaAgent | `bible_apocrypha` | Deuterocanonical texts (KJVA) |
| SummaryAgent | -- | Synthesizes all perspectives into a cohesive comparative essay |

### Morphological Keyword Search

Root-based search that goes beyond string matching to find all morphological derivatives of a root across the corpus.

| Scripture | Input | Approach |
|-----------|-------|----------|
| **Quran** | Arabic (كتب) or Buckwalter Latin (ktb) | Root extraction via PostgreSQL lookup (77,429 words, 1,651 roots) |
| **Bible OT** | Hebrew or transliteration (torah, chesed) | Strong's Concordance with Hebrew roots and b/v dual-indexing |
| **Bible NT** | Greek or transliteration (agape, logos) | Strong's Concordance with Greek lemma mapping |

Results include surah/chapter distribution charts, frequency counts, and verse-level context for every occurrence.

### Etymology Database

Clarus ships an Arabic root etymology database covering all 1,651 Quranic roots with definitions, morphological analysis, and cross-references to Lane's Lexicon.

| Field | Description | Source |
|-------|-------------|--------|
| **Root (Arabic)** | Original Arabic root | Quranic Arabic Corpus v0.4 |
| **Root (Buckwalter)** | Latin transliteration | Quranic Arabic Corpus v0.4 |
| **English Definition** | Lane's Lexicon definition | Lane's Arabic-English Lexicon (1863) |
| **Turkish Definition** | Quranic context translation | LLM-generated (Gemini 2.5 Flash) |
| **Morphological Forms** | Verb/noun pattern analysis | Extracted from `qm_words` |
| **Quran Frequency** | Occurrence count in Quran | Quranic Arabic Corpus v0.4 |

**Data Sources & Academic Citations:**

- **Quranic Arabic Corpus v0.4** — University of Leeds (GNU GPL)
  - Dukes, K. & Habash, N. (2010). "Morphological Annotation of Quranic Arabic." *LREC 2010*.
  - 77,429 words, 1,651 unique roots
- **Lane's Arabic-English Lexicon** — Edward William Lane (1863), digitized by Perseus/Tufts University (GPL-3.0)
  - 47,919 entries, 5,160 roots in PostgreSQL
  - Matches 1,337 of 1,651 Quranic roots (81%)
- **Turkish Definitions** — Generated via Google Gemini 2.5 Flash (OpenRouter)
  - Confidence scores (0.0-1.0) included per translation
  - Translations use Quranic/Islamic Turkish terminology
  - 314 corpus-only roots receive LLM-generated definitions (no English source available)
  - Not manually verified by human scholars

> **Note:** The etymology data is GPL-licensed due to the source licenses of the Quranic Arabic Corpus and Lane's Lexicon.

### Internationalization (i18n)

Full Turkish/English localization across the entire stack:

| Component | Implementation |
|-----------|----------------|
| **Frontend** | next-intl with namespace-based message catalogs (TR/EN) |
| **Backend** | Locale-aware error messages with Accept-Language header support |
| **LLM Cache** | Locale-aware cache keys prevent cross-language cache hits |
| **SEO** | hreflang tags, locale-aware metadata, and language switch navigation |
| **Testing** | Translation completeness and quality checks |

### Production Infrastructure

- **Authentication** — [Better Auth](https://www.better-auth.com/) with JWT + Google OAuth + API key support for CLI access
- **Caching** — Redis Stack 7.2 with LLM semantic cache, embedding cache, and fail-open resilience (app works without Redis)
- **Streaming** — Server-Sent Events for token-by-token response delivery with real-time progress indicators
- **Observability** — Structured logging with correlation IDs, Sentry error tracking, performance spans
- **Resilience** — Circuit breakers (pybreaker) + tenacity retries for all external service calls
- **Code Quality** — 11 pre-commit hooks (Ruff, ESLint, Prettier, Pyright, TypeScript, gitleaks, codespell)
- **CI/CD** — GitHub Actions with lint, format, typecheck, and test gates on every push and PR

---

## 🏗️ Architecture

```mermaid
graph LR
  subgraph Frontend
    A[Next.js 16 / React 19] --> B[TanStack Query]
    B --> C[SSE Streaming]
  end
  subgraph Backend
    D[FastAPI] --> E[Query Enhancement]
    E --> F[Multi-Query 3-5x]
    F --> G[Parallel Search]
    G --> H[RRF Fusion k=60]
    H --> I[Multi-Agent System]
  end
  subgraph Data
    J[(Qdrant - 123K vectors)]
    K[(PostgreSQL - Morphology)]
    L[(Redis - Cache/Rate)]
  end
  C --> D
  G --> J
  I --> K
  D --> L
```

### RAG Pipeline (Step by Step)

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Query Enhancement (Gemini 2.5 Flash)                    │
│     Expand with synonyms, related concepts, cross-language  │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Multi-Query Generation (3-5 variants)                   │
│     Diverse phrasings to maximize recall                    │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Parallel Semantic Search (all collections)              │
│     Dense vectors (text-embedding-3-large, 3072-dim)        │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  4. RRF Fusion (k=60)                                       │
│     Merge multi-query results into single ranked list       │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Multi-Agent Synthesis (Gemini 2.5 Flash)                │
│     [QuranAgent, OTAgent, NTAgent, ApocryphaAgent]          │
│                         │                                   │
│                    SummaryAgent                             │
│                         │                                   │
│                  Comparative Essay                          │
└─────────────────────────────────────────────────────────────┘
```

### 5-Agent Pipeline

```
                    ┌─────────────────┐
                    │   User Query    │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │ QuranAgent  │   │  OTAgent    │   │  NTAgent    │
   │ quran_tr_*  │   │  bible_ot   │   │  bible_nt   │
   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
          │                  │                  │
          │         ┌────────┴────────┐         │
          │         │ ApocryphaAgent  │         │
          │         │ bible_apocrypha │         │
          │         └────────┬────────┘         │
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │  SummaryAgent   │
                    │  (synthesizes)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Comparative     │
                    │ Essay (5 paras) │
                    └─────────────────┘
```

---

## 📦 Collections

| Collection | Verses | Language | Source |
|------------|--------|----------|--------|
| `quran_tr_diyanet` | 6,236 | Turkish | Diyanet Isleri translation |
| `quran_tr_yazir` | 6,236 | Turkish | Elmalili Hamdi Yazir |
| `quran_tr_ates` | 6,236 | Turkish | Suleyman Ates |
| `quran_tr_bulac` | 6,236 | Turkish | Ali Bulac |
| `quran_tr_ozturk` | 6,236 | Turkish | Yasar Nuri Ozturk |
| `quran_tr_vakfi` | 6,236 | Turkish | Diyanet Vakfi |
| `quran_tr_yildirim` | 6,236 | Turkish | Suat Yildirim |
| `quran_tr_yuksel` | 6,236 | Turkish | Edip Yuksel |
| `bible_ot` | 23,145 | English | Old Testament (KJVA) |
| `bible_nt` | 7,957 | English | New Testament (KJVA) |
| `bible_apocrypha` | 5,717 | English | Apocrypha (KJVA) |
| `bible_tr_ot` | 22,724 | Turkish | Old Testament (Turkish) |
| `bible_tr_nt` | 7,458 | Turkish | New Testament (Turkish) |

**Total: ~123,000 indexed vectors across 13 collections**

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend runtime |
| Docker | Latest | Qdrant, PostgreSQL, Redis |
| [uv](https://docs.astral.sh/uv/) | Latest | Python package manager |

### 1. Clone & Install

```bash
git clone https://github.com/aliozdenisik/Clarus.git
cd Clarus

# Backend
cd backend
uv sync
cd ..

# Frontend
cd frontend
npm install
cd ..
```

### 2. Configure Environment

Create `backend/.env`:

```env
# Required
OPENROUTER_API_KEY=your-openrouter-key

# Database (Docker defaults work out of the box)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:54322/postgres

# Better Auth (for web UI authentication)
BETTER_AUTH_JWKS_URL=http://localhost:3000/api/auth/jwks
BETTER_AUTH_ISSUER=http://localhost:3000

# Rate limiting (default in backend config is true)
# Set to false locally if you need to disable limits during development/testing
RATE_LIMIT_ENABLED=false
```

Create `frontend/.env.local`:

```env
BETTER_AUTH_DATABASE_URL=postgresql://postgres:postgres@localhost:54322/postgres

# Generate a random 32+ character secret for session signing
# Run: openssl rand -base64 32
BETTER_AUTH_SECRET=your-random-secret-replace-with-generated-value

NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000

# Optional: Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

**Generate the auth secret:**

```bash
# macOS/Linux
openssl rand -base64 32

# Or use Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

### 3. Start Infrastructure

```bash
# Start PostgreSQL + Qdrant + Redis
docker compose up -d

# Index all collections (first time only, ~2 minutes)
cd backend
uv run python scripts/setup_all_collections.py

# Verify
uv run python main.py info
```

### 4. Run

```bash
# Option A: Full stack (API + Web UI)
cd backend && uvicorn app.main:app --reload &
cd frontend && npm run dev &

# Option B: CLI only
cd backend
uv run python main.py search "sabir ve namaz"
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Qdrant Dashboard | http://localhost:6333/dashboard |
| Redis Insight | http://localhost:8001 |

---

## 📖 Usage

### CLI

```bash
cd backend

# Search
uv run python main.py search "sabir ve namaz"                    # Quran (default: Diyanet)
uv run python main.py search --translator yazir "sabir"          # Quran (Yazir translation)
uv run python main.py search-bible "love your neighbor"          # Bible (KJVA)

# Question & Answer
uv run python main.py ask "Islam'da sabir nedir?"                # Quran Q&A
uv run python main.py ask-bible "What is love?"                  # Bible Q&A

# Comparative Analysis
uv run python main.py compare "The concept of forgiveness"       # Single essay
uv run python main.py compare --multi-agent "The creation story" # 5-agent analysis

# Morphological Keyword Search
uv run python main.py keyword-search "كتب"                      # Arabic root
uv run python main.py keyword-search "ktb"                       # Buckwalter Latin
uv run python main.py bible-keyword-search "torah"               # Hebrew transliteration
uv run python main.py bible-keyword-search "G2316"               # Greek Strong's number

# System
uv run python main.py info                                       # Collection stats
uv run python main.py cache-info                                 # Cache stats
uv run python main.py cache-clear                                # Clear cache
```

### Python API

```python
import asyncio
from src.ultimate_rag import UltimateRAG
from src.comparative_rag import ComparativeRAG

async def main():
    # Semantic search
    rag = UltimateRAG(enable_semantic_chunks=True)
    results = await rag.search_quran("intercession concept", top_k=5)
    answer = await rag.ask_bible("What is forgiveness?")

    # Multi-agent comparative analysis
    comp = ComparativeRAG()
    result = await comp.compare_multi_agent("Creation and the origin of humanity")
    print(result["paragraphs"])

asyncio.run(main())
```

### Screenshots

<table>
  <tr>
    <td align="center"><strong>Semantic Search</strong></td>
    <td align="center"><strong>Comparative Analysis</strong></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/readme-search.png" alt="Search" width="500"/></td>
    <td><img src="docs/screenshots/readme-compare.png" alt="Compare" width="500"/></td>
  </tr>
  <tr>
    <td align="center"><strong>Morphological Word Search</strong></td>
    <td align="center"><strong>Quran Browse</strong></td>
  </tr>
  <tr>
    <td><img src="docs/screenshots/readme-keyword-search.png" alt="Keyword Search" width="500"/></td>
    <td><img src="docs/screenshots/readme-quran-browse.png" alt="Quran Browse" width="500"/></td>
  </tr>
</table>

---

## 📡 API Reference

Full OpenAPI documentation is available at `/docs` when the server is running.

### Search

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/search/quran` | POST | Quran semantic search with translator selection | Yes |
| `/api/search/bible` | POST | Bible semantic search (OT/NT/Apocrypha) | Yes |
| `/api/stream/search` | GET | SSE streaming search | Yes |
| `/api/enhance/` | POST | Query enhancement preview | Yes |

### Compare

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/compare/` | POST | Multi-agent comparative analysis | Yes |
| `/api/stream/compare` | GET | SSE streaming compare | Yes |

### Keyword & Morphology

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/search/keyword/` | POST | Quran morphological root search | -- |
| `/api/search/keyword/roots` | GET | List all Arabic roots (paginated) | -- |
| `/api/search/bible-keyword/` | POST | Bible morphological search | -- |
| `/api/etymology/` | GET | Arabic root etymology from Lane's Lexicon | -- |

### Verse Lookup

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/verse-lookup/` | POST | Lookup verse by reference | Yes |
| `/api/verse-translations/` | GET | Get verse in all 8 Quran translations | Yes |

### Auth & User

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/api-key` | POST | Generate CLI API key |
| `/api/auth/me` | GET | Current user info |
| `/api/auth/rate-limit` | GET | Rate limit status |

### Metadata & Health

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/metadata/collections` | GET | Qdrant collection stats |
| `/api/metadata/quran/surahs` | GET | All 114 surahs |
| `/api/metadata/bible/books` | GET | All Bible books |
| `/api/health` | GET | Health check (Qdrant, Redis, event loop) |
| `/docs` | GET | OpenAPI / Swagger UI |

---

## 🛠️ Tech Stack

### Backend

| Component | Technology |
|-----------|------------|
| Framework | FastAPI (async) + SQLAlchemy 2.0 |
| Runtime | Python 3.11+ with [uv](https://docs.astral.sh/uv/) |
| Vector DB | Qdrant (HNSW + Scalar Quantization) |
| Database | PostgreSQL 15 |
| Cache | Redis Stack 7.2 (LLM semantic cache, search cache, JWT blacklist) |
| Encoder | OpenAI text-embedding-3-large (3072-dim) |
| LLM (Enhancement) | Gemini 2.5 Flash via OpenRouter |
| LLM (Generation) | Gemini 2.5 Flash via OpenRouter |
| LLM (Translation) | Gemini 2.5 Flash Lite via OpenRouter |
| Auth | Better Auth (JWT + Google OAuth + JWKS) |
| Observability | Sentry + structured logging + correlation IDs |
| Resilience | Circuit breakers (pybreaker) + tenacity retries |

### Frontend

| Component | Technology |
|-----------|------------|
| Framework | Next.js 16 (App Router) |
| Runtime | React 19, TypeScript 5 |
| Styling | Tailwind CSS 4 + Radix UI primitives |
| Animation | Framer Motion 12 |
| State | Zustand 5 + TanStack Query 5 + nuqs |
| API Client | Generated via @hey-api/openapi-ts |
| Auth UI | @daveyplate/better-auth-ui |
| Testing | Vitest 4 + React Testing Library (228+ tests) |
| E2E | Playwright |
| Charts | Recharts 3 |
| i18n | next-intl (EN, TR) |

### Infrastructure

| Component | Technology |
|-----------|------------|
| Containers | Docker Compose (PostgreSQL + Qdrant + Redis) |
| CI | GitHub Actions (lint, format, typecheck, test) |
| Pre-commit | 11 hooks (Ruff, ESLint, Prettier, gitleaks, codespell, etc.) |
| Linting | Ruff (20 rule sets) + ESLint 9 |
| Formatting | Ruff (Python) + Prettier (TypeScript) |
| Type Checking | Pyright + TypeScript strict |

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Quran Recall | **80%+** |
| Bible Recall | **100%** |
| Confidence Score | **96%** |
| Multi-Agent Latency | ~40s |
| Cost per Query | ~$0.013 (with semantic cache) |
| Cache Hit Rate | 60-80% reduction in API costs |
| Indexed Vectors | ~123,000 across 13 collections |
| Morphology DB | 77,429 words, 1,651 roots |

Recall is measured against a ground-truth dataset (`backend/tests/test_data.json`) using F1 score. The semantic cache is the single biggest cost lever: repeated or semantically similar queries skip the LLM entirely and return cached results within milliseconds.

---

## 🧪 Testing

### Frontend

```bash
cd frontend
npm test                          # Vitest (228+ tests, 21 files)
npm run test:e2e                  # Playwright E2E
npx tsc --noEmit                  # Type check
```

### Backend

```bash
cd backend
uv run pytest tests/ -v           # Unit tests
uv run ruff check .               # Lint
uv run ruff format --check .      # Format check
uv run pyright                    # Type check
```

### Pre-commit Hooks

```bash
# Install (one-time)
pre-commit install
pre-commit install --hook-type pre-push

# Run on all files
pre-commit run --all-files
```

The pre-commit suite runs 11 hooks: Ruff lint + format, ESLint, Prettier, Pyright, TypeScript `noEmit`, gitleaks (secret scanning), codespell, and trailing whitespace checks. All hooks run on every commit; the push hooks run the full type-check suite.

---

## 📁 Project Structure

```
Clarus/
├── backend/                        # Python FastAPI + RAG pipeline
│   ├── main.py                     # CLI entrypoint (Rich formatting, 1,871 lines)
│   ├── app/                        # FastAPI application
│   │   ├── main.py                 # ASGI server
│   │   ├── api/                    # Route handlers (15 endpoints)
│   │   ├── auth/                   # JWKS validator + API key auth
│   │   ├── i18n/                   # Locale detection + message catalogs
│   │   ├── middleware/             # CORS, correlation ID, error handling
│   │   ├── schemas/                # Pydantic models (4 files)
│   │   └── config.py               # Settings
│   ├── src/                        # RAG pipeline modules (29 files)
│   │   ├── ultimate_rag.py         # Core RAG pipeline (1,447 lines)
│   │   ├── comparative_rag.py      # 4-collection parallel search + RRF (1,414 lines)
│   │   ├── multi_agent_answer_generator.py  # 5-agent system (805 lines)
│   │   ├── bible_morphology.py     # Hebrew/Greek Strong's search (1,900 lines)
│   │   ├── search.py               # Qdrant semantic search (880 lines)
│   │   ├── quran_morphology.py     # Arabic root-based keyword search (607 lines)
│   │   ├── query_enhancer.py       # LLM query expansion (729 lines)
│   │   ├── query_translator.py     # Multilingual translation, 8 languages (613 lines)
│   │   ├── embeddings.py           # OpenAI dense encoder (570 lines)
│   │   ├── confidence_scorer.py    # Two-phase sigmoid-calibrated scoring (376 lines)
│   │   ├── semantic_chunker.py     # Quran verse grouping (638 lines)
│   │   ├── bible_semantic_chunker.py  # Bible verse grouping (499 lines)
│   │   └── ...                     # 17 more modules
│   ├── data/                       # Source data (quran_tr.json, bible_kjva.json)
│   ├── tests/                      # Pytest + accuracy benchmarks
│   └── scripts/                    # Setup & migration scripts
├── frontend/                       # Next.js 16 + React 19
│   ├── app/                        # App Router with [locale] (17 routes)
│   ├── components/                 # UI components (60+ files)
│   │   ├── ui/                     # Radix primitives (33 files)
│   │   ├── compare/                # Comparative analysis UI (7 files)
│   │   ├── keyword-search/         # Morphological search UI (12 files)
│   │   ├── quran/                  # Quran-specific components
│   │   ├── verse-lookup/           # Verse reference lookup
│   │   └── search/                 # Search components
│   ├── lib/                        # API client, hooks, stores (35 files)
│   │   ├── api/                    # Generated TypeScript client (2,054-line types)
│   │   ├── stores/                 # Zustand state management
│   │   ├── auth/                   # Better Auth integration
│   │   └── i18n/                   # next-intl configuration
│   ├── messages/                   # TR/EN translation files
│   └── __tests__/                  # Vitest + RTL (21 files, 228+ tests)
├── docs/
│   ├── screenshots/                # UI screenshots
│   └── technical/                  # Technical documentation
├── docker-compose.yml              # PostgreSQL + Qdrant + Redis
├── .pre-commit-config.yaml         # 11 hooks for code quality
├── .github/workflows/              # CI pipelines
└── memory-bank/                    # Project context and decisions
```

---

## 🔧 Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Yes | -- | OpenRouter API key for all LLM calls |
| `DATABASE_URL` | Yes | -- | PostgreSQL connection string (asyncpg) |
| `BETTER_AUTH_JWKS_URL` | -- | `http://localhost:3000/api/auth/jwks` | Better Auth JWKS endpoint |
| `BETTER_AUTH_ISSUER` | -- | `http://localhost:3000` | JWT issuer URL |
| `REDIS_URL` | -- | `redis://localhost:6379` | Redis connection string |
| `RATE_LIMIT_PER_DAY` | -- | `50` | Queries per user per day |
| `RATE_LIMIT_ENABLED` | -- | `true` | Rate limiting toggle |
| `LOG_LEVEL` | -- | `INFO` | Logging level |
| `LOG_FORMAT` | -- | `console` | `console` (dev) or `json` (prod) |
| `SENTRY_DSN_BACKEND` | -- | -- | Sentry DSN for backend error tracking |

### Frontend (`frontend/.env.local`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BETTER_AUTH_DATABASE_URL` | Yes | -- | PostgreSQL connection for Better Auth |
| `BETTER_AUTH_SECRET` | Yes | -- | Random 32+ char secret for session signing |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | -- | `http://localhost:3000` | Better Auth base URL |
| `GOOGLE_CLIENT_ID` | -- | -- | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | -- | -- | Google OAuth client secret |
| `NEXT_PUBLIC_SENTRY_DSN` | -- | -- | Sentry DSN for frontend error tracking |

---

## 📚 Technical Documentation

Deep-dive papers covering the algorithms and design decisions behind Clarus:

| Document | Description |
|----------|-------------|
| [Multi-Query Search & RRF Fusion](docs/technical/hybrid-search-and-rrf-fusion.md) | Mathematical foundations of semantic vector search and Reciprocal Rank Fusion |
| [Confidence Scoring System](docs/technical/confidence-scoring-system.md) | Two-phase sigmoid-calibrated scoring with Platt scaling |
| [Morphological Analysis Pipeline](docs/technical/morphological-analysis-pipeline.md) | Computational linguistics for Arabic, Hebrew, and Greek sacred texts |
| [Multi-Agent RAG Architecture](docs/technical/multi-agent-rag-architecture.md) | 5-agent parallel search and synthesis system design |
| [Semantic Chunking Algorithms](docs/technical/semantic-chunking-algorithms.md) | Embedding-based verse grouping with boundary detection |
| [Caching & Resilience Patterns](docs/technical/caching-and-resilience-patterns.md) | Redis architecture, circuit breakers, and fail-open design |

---

## 🤝 Contributing

Contributions are welcome. The project uses strict code quality enforcement via pre-commit hooks and CI gates.

### Setup

```bash
# Install pre-commit hooks (runs automatically on every commit)
pip install pre-commit
pre-commit install
pre-commit install --hook-type pre-push
```

### Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make changes (pre-commit hooks enforce formatting and linting automatically)
4. Run tests (`cd frontend && npm test` and `cd backend && uv run pytest`)
5. Push and open a Pull Request

### Code Standards

- **Python**: Ruff (20 rule sets), Pyright strict, async-first design
- **TypeScript**: ESLint 9, Prettier, strict `noEmit` type checking
- No `any` in TypeScript; no `# type: ignore` in Python without justification
- Structured logging only -- no `console.log` or bare `print()` in production code
- All Qdrant/LLM/Redis calls must be async with explicit error handling

---

## 📄 License

This project is licensed under the MIT License -- see the [LICENSE](LICENSE) file for details.

The etymology database (Arabic roots, Lane's Lexicon data) is GPL-licensed due to upstream source licenses.

---

<div align="center">

Built with [Qdrant](https://qdrant.tech), [FastAPI](https://fastapi.tiangolo.com), [Next.js](https://nextjs.org), and [OpenRouter](https://openrouter.ai)

**[Back to Top](#clarus)**

</div>
