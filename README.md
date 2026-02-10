<div align="center">

# Clarus

**Maximum-accuracy RAG search engine for sacred texts**

Comparative theological analysis across Quran and Bible with multi-agent LLM synthesis, morphological keyword search, and multilingual support.

[![Backend CI](https://github.com/aliozdenisik/Clarus/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/aliozdenisik/Clarus/actions/workflows/backend-ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&style=flat-square)](https://github.com/pre-commit/pre-commit)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776ab.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000.svg?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-DC382D.svg?style=flat-square&logo=qdrant&logoColor=white)](https://qdrant.tech)
[![Redis](https://img.shields.io/badge/Redis-DC382D.svg?style=flat-square&logo=redis&logoColor=white)](https://redis.io)

[Features](#-features) · [Quick Start](#-quick-start) · [Architecture](#-architecture) · [Usage](#-usage) · [API](#-api-reference) · [Contributing](#-contributing)

</div>

## Overview

Clarus is a production-ready Retrieval-Augmented Generation (RAG) system for **maximum retrieval accuracy** on religious texts. It combines hybrid search (dense + sparse vectors) with multi-agent LLM synthesis to provide scholarly-quality comparative analysis across the Quran (8 Turkish translations) and Bible (English KJVA + Turkish).

### Key Highlights

- **Hybrid Search** — Dense embeddings (OpenAI text-embedding-3-large) + BM25 sparse vectors fused via Reciprocal Rank Fusion
- **5-Agent Synthesis** — Specialized agents for Quran, OT, NT, and Apocrypha, unified by a Summary agent into cohesive essays
- **Morphological Keyword Search** — Root-based Arabic (كتب) and Hebrew/Greek concordance with Strong's numbers
- **Multilingual** — Query in 8 languages (TR, EN, ES, FR, IT, PT, AR, DE) with automatic detection and translation
- **Production Ready** — Better Auth, Redis caching, rate limiting, SSE streaming, Sentry observability, pre-commit hooks

---

## ✨ Features

### Search & Retrieval

| Feature | Description |
|---------|-------------|
| **Hybrid Search** | Dense vectors (3072-dim) + BM25 sparse vectors across all collections |
| **Semantic Chunking** | Context-aware verse grouping that preserves scriptural boundaries |
| **Query Enhancement** | LLM-powered query expansion with synonym and concept injection |
| **Multi-Query RAG** | 3-5 query variants per request for maximum recall |
| **RRF Fusion** | Reciprocal Rank Fusion (k=60) combining dense + sparse scores |

### Multi-Agent Comparative Analysis

```
Query --> [QuranAgent, OTAgent, NTAgent, ApocryphaAgent] --> SummaryAgent --> Essay
```

Each agent searches its own collection, generates commentary, and the Summary agent synthesizes all perspectives into a structured 5-paragraph essay with inline citations.

### Morphological Keyword Search

| Scripture | Input | Approach |
|-----------|-------|----------|
| **Quran** | Arabic (كتب) or Buckwalter Latin (ktb) | Root extraction via PostgreSQL lookup (77K words, 1,651 roots) |
| **Bible OT** | Hebrew or transliteration (torah, chesed) | Strong's Concordance with Hebrew roots and b/v dual-indexing |
| **Bible NT** | Greek or transliteration (agape, logos) | Strong's Concordance with Greek lemma mapping |

### Etymology Database

Clarus includes an Arabic root etymology database for all 1,651 Quranic roots, providing definitions, morphological analysis, and cross-references.

| Field | Description | Source |
|-------|-------------|--------|
| **Root (Arabic)** | Original Arabic root | Quranic Arabic Corpus v0.4 |
| **Root (Buckwalter)** | Latin transliteration | Quranic Arabic Corpus v0.4 |
| **English Definition** | Lane's Lexicon definition | Lane's Arabic-English Lexicon (1863) |
| **Turkish Definition** | Quranic context translation | LLM-generated (Gemini 2.5 Flash) |
| **Morphological Forms** | Verb/noun pattern analysis | Extracted from qm_words |
| **Quran Frequency** | Occurrence count in Quran | Quranic Arabic Corpus v0.4 |

**Data Sources & Citations:**

- **Quranic Arabic Corpus v0.4** — University of Leeds (GNU GPL)
  - Dukes, K. & Habash, N. (2010). "Morphological Annotation of Quranic Arabic." *LREC 2010*.
  - 77,429 words, 1,651 unique roots
- **Lane's Arabic-English Lexicon** — Edward William Lane (1863), digitized by Perseus/Tufts University (GPL-3.0)
  - 47,919 entries, 5,160 roots in PostgreSQL
  - Matches 1,337 of 1,651 Quranic roots (81%)
- **Turkish Translations** — Generated via Google Gemini 2.5 Flash (OpenRouter)
  - ⚠️ LLM-generated, not manually verified by human scholars
  - Confidence scores (0.0–1.0) included per translation
  - Translations use Quranic/Islamic Turkish terminology
  - 314 corpus-only roots receive LLM-generated definitions (no English source)

> **Note:** The etymology data is GPL-licensed due to the source licenses of the Quranic Arabic Corpus and Lane's Lexicon.

### Multi-Agent System

| Agent | Collection | Role |
|-------|------------|------|
| QuranAgent | `quran_tr_*` | Quran perspective and commentary |
| OldTestamentAgent | `bible_ot` | Old Testament (Torah, Prophets, Writings) |
| NewTestamentAgent | `bible_nt` | New Testament (Gospels, Epistles) |
| ApocryphaAgent | `bible_apocrypha` | Deuterocanonical texts |
| SummaryAgent | -- | Synthesizes all perspectives into cohesive essay |

### Production Infrastructure

- **Authentication** — [Better Auth](https://www.better-auth.com/) with JWT + Google OAuth + API key support for CLI
- **Caching** — Redis Stack 7.2 with semantic cache (theta=0.95), embedding cache, rate limiting, and fail-open resilience
- **Streaming** — Server-Sent Events for token-by-token response delivery
- **Observability** — Structured logging with correlation IDs, Sentry error tracking, performance spans
- **Code Quality** — 11 pre-commit hooks (Ruff, ESLint, Prettier, Pyright, TypeScript, gitleaks, codespell)
- **CI/CD** — GitHub Actions with lint, format, typecheck, and test gates

---

## 🏗️ Architecture

```
                                 Clarus Architecture

   ┌──────────────┐      ┌──────────────┐      ┌──────────────────────────────┐
   │   Next.js 16 │      │   FastAPI    │      │        Data Stores           │
   │   React 19   │─────>│   Python    │─────>│                              │
   │   Port 3000  │ JWT  │   Port 8000  │      │  Qdrant (6333)  13 collections│
   └──────────────┘      └──────┬───────┘      │  PostgreSQL (54322)          │
                                │              │  Redis Stack (6379)          │
                                v              └──────────────────────────────┘
                     ┌──────────────────┐
                     │   RAG Pipeline   │
                     ├──────────────────┤
                     │ 1. Query Enhance │──> Grok 4.1 Fast
                     │ 2. Multi-Query   │──> 3-5 variants
                     │ 3. Parallel      │──> 13 collections (dense + sparse)
                     │    Search        │
                     │ 4. RRF Fusion    │──> k=60
                     │ 5. Multi-Agent   │──> 5 agents via Gemini 2.5 Flash
                     └──────────────────┘
```

### Collections

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

**Total:** ~123,000 indexed vectors across 13 collections

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
```

Create `frontend/.env.local`:

```env
BETTER_AUTH_DATABASE_URL=postgresql://postgres:postgres@localhost:54322/postgres
BETTER_AUTH_SECRET=your-random-secret
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000

# Optional: Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
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
uv run python main.py search --translator yazir "sabir"           # Quran (Yazir translation)
uv run python main.py search-bible "love your neighbor"           # Bible (KJVA)

# Question & Answer
uv run python main.py ask "Islam'da sabir nedir?"                 # Quran Q&A
uv run python main.py ask-bible "What is love?"                   # Bible Q&A

# Comparative Analysis
uv run python main.py compare "The concept of forgiveness"        # Single essay
uv run python main.py compare --multi-agent "The creation story"  # 5-agent analysis

# Morphological Keyword Search
uv run python main.py keyword-search "كتب"                       # Arabic root
uv run python main.py keyword-search "ktb"                        # Buckwalter Latin
uv run python main.py bible-keyword-search "torah"                # Hebrew transliteration
uv run python main.py bible-keyword-search "G2316"                # Greek Strong's number

# System
uv run python main.py info                                        # Collection stats
uv run python main.py cache-info                                  # Cache stats
uv run python main.py cache-clear                                 # Clear cache
```

### Python API

```python
import asyncio
from src.ultimate_rag import UltimateRAG
from src.comparative_rag import ComparativeRAG

async def main():
    # Search
    rag = UltimateRAG(enable_semantic_chunks=True)
    results = await rag.search_quran("intercession concept", top_k=5)
    answer = await rag.ask_bible("What is forgiveness?")

    # Comparative Analysis
    comp = ComparativeRAG()
    result = await comp.compare_multi_agent("Creation and the origin of humanity")
    print(result["paragraphs"])

asyncio.run(main())
```

---

## 📡 API Reference

Full OpenAPI documentation is available at `/docs` when the server is running.

### Core Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/search/quran` | POST | Quran search with translator selection | Yes |
| `/api/search/bible` | POST | Bible search (OT/NT/Apocrypha) | Yes |
| `/api/compare/` | POST | Multi-agent comparative analysis | Yes |
| `/api/stream/search` | GET | SSE streaming search | Yes |
| `/api/stream/compare` | GET | SSE streaming compare | Yes |
| `/api/search/keyword/` | POST | Quran morphological root search | -- |
| `/api/search/keyword/roots` | GET | List all Arabic roots (paginated) | -- |
| `/api/search/bible-keyword/` | POST | Bible morphological search | -- |
| `/api/enhance/` | POST | Query enhancement preview | Yes |

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
| Database | PostgreSQL 15 (Supabase) |
| Cache | Redis Stack 7.2 (semantic cache, rate limiting, JWT blacklist) |
| Dense Encoder | OpenAI text-embedding-3-large (3072-dim) |
| Sparse Encoder | BM25 via FastEmbed |
| LLM (Enhancement) | Grok 4.1 Fast via OpenRouter |
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

---

## 📁 Project Structure

```
Clarus/
├── backend/                        # Python FastAPI + RAG pipeline
│   ├── main.py                     # CLI entrypoint (Rich formatting)
│   ├── app/                        # FastAPI application
│   │   ├── main.py                 # ASGI server
│   │   ├── api/                    # Route handlers (13 endpoints)
│   │   ├── auth/                   # JWKS validator + API key auth
│   │   ├── middleware/             # CORS, rate limiting, correlation ID
│   │   ├── schemas/                # Pydantic models
│   │   └── config.py               # Settings
│   ├── src/                        # RAG pipeline modules (29 files)
│   │   ├── ultimate_rag.py         # Core RAG pipeline
│   │   ├── comparative_rag.py      # 4-collection parallel search + RRF
│   │   ├── multi_agent_answer_generator.py  # 5-agent system
│   │   ├── search.py               # Qdrant hybrid search
│   │   ├── quran_morphology.py     # Arabic root-based keyword search
│   │   ├── bible_morphology.py     # Hebrew/Greek Strong's search
│   │   ├── query_translator.py     # Multilingual translation (8 languages)
│   │   ├── embeddings.py           # OpenAI + BM25 encoders
│   │   └── ...
│   ├── data/                       # Source data (JSON, XML)
│   ├── tests/                      # Pytest + accuracy benchmarks
│   └── scripts/                    # Setup & migration scripts
├── frontend/                       # Next.js 16 + React 19
│   ├── app/                        # App Router pages (17 routes)
│   ├── components/                 # UI components (60+ files)
│   │   ├── ui/                     # Radix primitives (33 files)
│   │   ├── compare/                # Comparative analysis UI
│   │   ├── keyword-search/         # Morphological search UI (12 files)
│   │   └── search/                 # Search components
│   ├── lib/                        # API client, hooks, stores
│   │   ├── api/                    # Generated TypeScript client
│   │   ├── stores/                 # Zustand state management
│   │   └── auth/                   # Better Auth integration
│   └── __tests__/                  # Vitest + RTL (21 files, 228+ tests)
├── docker-compose.yml              # PostgreSQL + Qdrant + Redis
├── .pre-commit-config.yaml         # 11 hooks for code quality
├── .github/workflows/              # CI pipelines
└── memory-bank/                    # Project documentation
```

---

## 🔧 Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Yes | -- | OpenRouter API key for LLM calls |
| `DATABASE_URL` | Yes | -- | PostgreSQL connection string |
| `BETTER_AUTH_JWKS_URL` | -- | `http://localhost:3000/api/auth/jwks` | Better Auth JWKS endpoint |
| `BETTER_AUTH_ISSUER` | -- | `http://localhost:3000` | JWT issuer |
| `REDIS_URL` | -- | `redis://localhost:6379` | Redis connection |
| `RATE_LIMIT_PER_DAY` | -- | `50` | Queries per user per day |
| `LOG_LEVEL` | -- | `INFO` | Logging level |
| `LOG_FORMAT` | -- | `console` | `console` (dev) or `json` (prod) |
| `SENTRY_DSN_BACKEND` | -- | -- | Sentry DSN for error tracking |

### Frontend (`frontend/.env.local`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BETTER_AUTH_DATABASE_URL` | Yes | -- | PostgreSQL for Better Auth |
| `BETTER_AUTH_SECRET` | Yes | -- | Random secret for session signing |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | -- | `http://localhost:3000` | Better Auth base URL |
| `GOOGLE_CLIENT_ID` | -- | -- | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | -- | -- | Google OAuth secret |
| `NEXT_PUBLIC_SENTRY_DSN` | -- | -- | Sentry DSN for frontend |

---

## 🤝 Contributing

Contributions are welcome! This project uses strict code quality enforcement.

### Setup

```bash
# Install pre-commit hooks (runs automatically on commit)
pip install pre-commit
pre-commit install
pre-commit install --hook-type pre-push
```

### Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make changes (pre-commit hooks enforce formatting and linting)
4. Run tests (`cd frontend && npm test` and `cd backend && uv run pytest`)
5. Push and open a Pull Request

### Code Standards

- **Python**: Ruff (20 rule sets), Pyright strict, async-first
- **TypeScript**: ESLint 9, Prettier, strict `noEmit` type checking
- **No `any`** in TypeScript, no `# type: ignore` in Python without justification
- **Structured logging** only -- no `console.log` or `print()` in production code

---

## 📄 License

This project is licensed under the MIT License -- see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built with Qdrant, FastAPI, Next.js, and OpenRouter

**[Back to Top](#clarus)**

</div>
