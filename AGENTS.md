# CLARUS - PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-10
**Commit:** 5d01c58
**Branch:** main

## OVERVIEW

Clarus is a maximum-accuracy RAG (Retrieval-Augmented Generation) search system for sacred texts (Quran in Turkish, Bible in English KJVA). Features 5-agent comparative theological analysis, semantic chunking, hybrid search with RRF fusion, and morphological keyword search with Arabic/Hebrew/Greek support.

## STRUCTURE

```
qdrant/                         # Root (project named after Qdrant DB it uses)
├── backend/                    # Python FastAPI + RAG pipeline
│   ├── main.py                 # CLI entrypoint (1871 lines - primary interface)
│   ├── app/                    # FastAPI REST API
│   │   ├── main.py             # ASGI server entrypoint
│   │   ├── api/                # Route handlers (13 files)
│   │   ├── auth/               # JWT + Google OAuth + token blacklist
│   │   ├── middleware/         # CORS, rate limiting, correlation ID, error handler
│   │   ├── schemas/            # Pydantic models (4 files)
│   │   ├── redis_client.py     # Redis connection management
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── config.py           # Settings
│   │   ├── db.py               # Database setup
│   │   └── logging_config.py   # Structured logging
│   ├── src/                    # RAG pipeline modules (29 files) ← CORE LOGIC
│   ├── tests/                  # Custom accuracy benchmarks (NOT pytest)
│   ├── scripts/                # Setup & dev scripts
│   └── data/                   # Source JSON (quran_tr.json, bible_kjva.json)
├── frontend/                   # Next.js 15 + Framer Motion
│   ├── app/                    # App Router pages (17 files)
│   ├── components/             # UI components (Radix + custom, 60+ files)
│   ├── lib/                    # API client, hooks, stores (35 files)
│   └── __tests__/              # Vitest + RTL tests (21 files)
├── memory-bank/                # Project context (READ FIRST)
├── docker-compose.yml          # PostgreSQL + Qdrant + Redis services
├── redis.conf                  # Redis configuration
├── start.sh / stop.sh          # Stack management scripts
└── qdrant_data/                # Qdrant persistent storage (43k vectors)
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add CLI command | `backend/main.py` | argparse + Rich formatting |
| Add API endpoint | `backend/app/api/` | FastAPI router pattern |
| Modify RAG pipeline | `backend/src/` | See `backend/src/AGENTS.md` |
| Add UI component | `frontend/components/` | Radix primitives + Framer Motion |
| Change auth flow | `backend/app/auth/` | JWT + OAuth + token blacklist |
| Update API client | `frontend/lib/api/` | Generated via @hey-api/openapi-ts |
| Add Pydantic schema | `backend/app/schemas/` | Organized by domain |
| Add middleware | `backend/app/middleware/` | CORS, rate limit, error handler |
| Modify Redis caching | `backend/app/redis_client.py` | Fail-open resilience |
| Add frontend test | `frontend/__tests__/` | Vitest + RTL (21 files) |
| Add keyword search component | `frontend/components/keyword-search/` | 12 components |
| Add compare component | `frontend/components/compare/` | 7 components |
| Project context | `memory-bank/` | Read `activeContext.md` first |

## CODE MAP

### Backend — Core RAG Pipeline (`backend/src/`)

| Module | Lines | Role |
|--------|-------|------|
| `bible_morphology.py` | 1900 | Bible morphological keyword search (Hebrew/Greek roots) |
| `ultimate_rag.py` | 1447 | Core RAG: enhance → multi-query → search → fuse → answer |
| `comparative_rag.py` | 1414 | 4-collection parallel search + RRF fusion |
| `search.py` | 880 | Qdrant hybrid search (dense+sparse) |
| `multi_agent_answer_generator.py` | 805 | 5-agent system (Quran, OT, NT, Apocrypha, Summary) |
| `verse_parser.py` | 792 | Verse reference parsing and normalization |
| `query_enhancer.py` | 729 | LLM query expansion with rate limiting |
| `indexer.py` | 644 | Qdrant collection management |
| `semantic_chunker.py` | 638 | Quran verse grouping |
| `query_translator.py` | 613 | Cross-language query translation |
| `quran_morphology.py` | 607 | Root-based morphological keyword search (Arabic) |
| `embeddings.py` | 570 | OpenAI text-embedding-3-large + BM25 |
| `greek_normalizer.py` | 509 | Greek text normalization + transliteration |
| `answer_generator.py` | 500 | Single-source LLM answers |
| `bible_semantic_chunker.py` | 499 | Bible verse grouping |
| `comparative_answer_generator.py` | 488 | Essay generation |
| `hebrew_normalizer.py` | 428 | Hebrew text normalization + transliteration |
| `llm_cache.py` | 395 | LLM response caching |
| `confidence_scorer.py` | 376 | Two-phase sigmoid-calibrated scoring |
| `bible_loader.py` | 282 | Bible KJVA loader |
| `lemmatizer.py` | 194 | Turkish text normalization |
| `turkish_utils.py` | 191 | Turkish-specific utilities |
| `data_loader.py` | 188 | Quran JSON loader |
| `circuit_breaker.py` | 142 | Circuit breaker for external services |
| `citation_sanitizer.py` | 126 | Citation format validation |
| `arabic_normalizer.py` | 87 | Arabic normalization + Buckwalter transliteration |
| `semantic_cache.py` | 38 | Semantic cache wrapper (Redis-backed) |
| `graph_rag.py` | 41 | Graph RAG placeholder |
| `multi_query.py` | 23 | Multi-query wrapper |

### Backend — API Layer (`backend/app/`)

| Module | Lines | Role |
|--------|-------|------|
| `api/compare.py` | 504 | Compare API + VerseDetail schema |
| `api/stream.py` | 501 | SSE streaming endpoints |
| `api/search.py` | 345 | Search API (Quran + Bible) |
| `api/auth.py` | 328 | JWT + Google OAuth endpoints |
| `api/compare_helpers.py` | 283 | Compare API helper functions |
| `api/metadata.py` | 274 | Collection metadata API |
| `api/verse_lookup.py` | 272 | Verse lookup by reference |
| `api/bible_keyword_search.py` | 250 | Bible keyword search REST API |
| `api/admin.py` | 209 | Admin endpoints |
| `api/keyword_search.py` | 152 | Quran keyword search REST API |
| `api/enhance.py` | 116 | Query enhancement endpoint |
| `api/preferences.py` | 116 | User preferences API |
| `logging_config.py` | 389 | Structured logging with correlation IDs |
| `models.py` | 252 | SQLAlchemy models |
| `middleware/rate_limit.py` | 211 | Redis sliding window rate limiting |
| `middleware/error_handler.py` | 160 | Global error handler |
| `redis_client.py` | 131 | Redis client with fail-open resilience |
| `config.py` | 81 | App configuration |
| `middleware/correlation.py` | 73 | Correlation ID middleware |
| `auth/token_blacklist.py` | 77 | JWT token blacklist (Redis) |
| `schemas/common.py` | 163 | Shared Pydantic models |
| `schemas/bible_keyword.py` | 120 | Bible keyword search schemas |
| `schemas/verse_lookup.py` | 78 | Verse lookup schemas |
| `schemas/keyword_search.py` | 73 | Keyword search schemas |

### Frontend (`frontend/`)

| Module | Lines | Role |
|--------|-------|------|
| `lib/api/types.gen.ts` | 2054 | Generated TypeScript API types |
| `app/compare/page.tsx` | 1070 | Multi-agent comparison UI |
| `lib/logger.ts` | 431 | Client-side structured logger |
| `lib/utils/parse-citations.ts` | 253 | Citation parsing utility |
| `components/keyword-search/root-browser.tsx` | 234 | Root morphology browser |
| `components/compare/analysis-progress.tsx` | 209 | Comparison progress indicator |
| `lib/auth/auth-context.tsx` | 196 | Auth context provider |
| `lib/hooks/use-sse.ts` | 188 | SSE hook for streaming |
| `components/keyword-search/verse-card.tsx` | 181 | Verse display card |
| `components/keyword-search/surah-chart.tsx` | 169 | Surah distribution chart |
| `lib/stores/preferences-store.ts` | 164 | Zustand preferences store |
| `components/keyword-search/accuracy-disclaimer.tsx` | 164 | Accuracy disclaimer |
| `components/verse-lookup/verse-lookup-input.tsx` | 135 | Verse lookup input component |
| `lib/utils/verse-url.ts` | 131 | Verse URL utilities |
| `lib/correlation.ts` | 119 | Correlation ID management |
| `components/compare/collection-selector.tsx` | 109 | Collection selector |
| `components/compare/source-reference-card.tsx` | 105 | Verse card with badge + text |
| `components/compare/citation-hover-card.tsx` | 98 | Citation hover tooltip |
| `components/keyword-search/search-input.tsx` | 91 | Search input component |
| `lib/stores/keyword-store.ts` | 82 | Zustand keyword search store |

## CONVENTIONS

### Python (backend/)
- **Imports**: Relative within `src/`, absolute for `app/`
- **Async**: All Qdrant/LLM/Redis calls are async
- **Error handling**: Explicit try-except with logging, no silent failures
- **Type hints**: Required on all function signatures
- **Redis**: Fail-open pattern — Redis failures never break the app

### TypeScript (frontend/)
- **Components**: Functional with explicit props interfaces
- **State**: Zustand stores in `lib/stores/`
- **API calls**: TanStack Query via generated client
- **Styling**: Tailwind + `cn()` utility from `lib/utils.ts`
- **Logging**: Structured logger in `lib/logger.ts` (not console.log)

### Naming
- Python: `snake_case` files, `PascalCase` classes
- TypeScript: `kebab-case` files, `PascalCase` components
- Collections: `quran_tr`, `bible_ot`, `bible_nt`, `bible_apocrypha`

## ANTI-PATTERNS (THIS PROJECT)

- **No `any` in TypeScript** - Types are generated from OpenAPI spec
- **No pytest** - Backend uses custom accuracy benchmark framework
- **No hardcoded API keys** - Must use `.env` file
- **No synchronous LLM calls** - Always async with timeout
- **No console.log in frontend** - Use structured logger
- **No silent Redis failures** - Fail-open with logging

## UNIQUE PATTERNS

### 5-Agent System
```
Query → [QuranAgent, OTAgent, NTAgent, ApocryphaAgent] → SummaryAgent → Essay
```
Each agent searches its collection, generates commentary. Summary agent synthesizes into 5-paragraph essay.

### Hybrid Search Pipeline
```
Query → LLM Enhancement → Multi-Query (3-5 variants) →
       Parallel Search (4 collections, dense+sparse) →
       RRF Fusion (k=60) → Rerank → Answer
```

### Morphological Keyword Search
```
Arabic Input (كتب) or Buckwalter (ktb) → Root Extraction →
       Derived Words → Verse Lookup → Surah Distribution
Hebrew/Greek Input → Strongs Number Mapping → Cross-reference
```

### Redis Infrastructure
```
Rate Limiting  → Sliding window per user (Redis)
Token Blacklist → JWT invalidation on logout (Redis)  
Search Cache   → Result caching with TTL (Redis)
Semantic Cache  → LLM response dedup (Redis)
Circuit Breaker → External service resilience
```

### Testing Strategy
- **Frontend**: Standard Vitest + RTL (`npm test`, 21 test files, 228+ passing tests)
- **Backend**: Pytest unit tests (`uv run pytest tests/`) + custom accuracy benchmarks
  - Pytest config excludes integration tests (run_*.py, *_verification_test.py)
  - CI runs on every push/PR via `.github/workflows/backend-ci.yml`
  - 5 previously excluded tests now fixed (health endpoint, verse bounds validation)
- **Accuracy Benchmarks**: `run_retrieval_accuracy_test.py` measures F1 score against `test_data.json` ground truth

### CI/CD Infrastructure
- **Backend CI**: `.github/workflows/backend-ci.yml` runs on push/PR
  - Lint with Ruff (`ruff check .`)
  - Format check (`ruff format --check .`)
  - Type check with Pyright (`pyright`)
  - Run pytest tests (`uv run pytest tests/ -v`)
  - All quality checks continue-on-error (non-blocking)
- **Package Manager**: Uses `uv` (Astral's fast Python package manager) for reproducible installs
- **Test Collection**: Filters exclude benchmark/integration scripts via `pyproject.toml`

### Frontend Performance Patterns
- **React Key Stability**: No index-based keys in dynamic lists (Issue #94)
  - Use data identity keys (`key={result.reference}`)
  - Composite keys for duplicates (`key={`${citation.reference}-${idx}`}`)
  - Namespaced skeleton keys (`key="root-browser-skeleton-${i}"`)
- **SSE Single-Pass Aggregation**: Process streaming messages once instead of multiple filter/map passes (Issue #92)
- **Zustand Selector-Based Subscriptions**: Narrow subscriptions prevent unnecessary re-renders (Issue #90)
- **React-Window Virtualization**: Render only visible rows for 1,600+ item lists (Issue #91)
- **Batched DOM Reads**: useLayoutEffect batches tab indicator geometry reads (Issue #91)
- **Cached Bounds**: Magnetic button caches getBoundingClientRect on mouseenter (Issue #91)
- **Bundle Optimization**: DevTools lazy-loaded in dev only, direct date-fns imports, Recharts code-split

## COMMANDS

```bash
# Infrastructure
docker compose up -d                    # Start Qdrant + PostgreSQL + Redis
./start.sh                              # Start full stack
./stop.sh                               # Stop full stack

# Backend (from backend/)
uv run python main.py search "sabir ve namaz"  # Quran search
python main.py ask "Islam'da sabir?"    # Q&A with citations
python main.py compare "Yaratilis"      # Multi-agent comparison
python main.py keyword-search "كتب"   # Arabic morphological root search
python main.py keyword-search "ktb"    # Buckwalter Latin input
python main.py info                     # Collection stats
uvicorn app.main:app --reload           # Start API server

# Frontend (from frontend/)
npm install
npm run dev                             # Dev server :3000
npm test                                # Run Vitest

# Full stack
./backend/scripts/dev.sh                # Starts everything
```

## NOTES

- **Rate limit**: 50 queries/day/user via Redis sliding window (configurable in `backend/app/config.py`)
- **Collections total**: 43,055 vectors (Quran 6,236 + Bible OT 23,145 + NT 7,957 + Apocrypha 5,717)
- **Morphology DB**: 77,429 words, 1,651 roots in PostgreSQL (qm_surahs, qm_ayahs, qm_words)
- **LLM costs**: ~$0.013/query with semantic cache (60-80% reduction)
- **Port conflicts**: Qdrant on 6333, PostgreSQL on 54322, Redis on 6379, API on 8000, Frontend on 3000
- **Redis**: Fail-open — app works without Redis (graceful degradation)
- **Backend .env loading**: `.env` loaded before LLM stack init in `backend/app/config.py` (critical for API keys)
- **Memory bank**: Always read `memory-bank/activeContext.md` before starting work

## CHILD AGENTS.md

- [`backend/src/AGENTS.md`](backend/src/AGENTS.md) - RAG pipeline internals
- [`frontend/AGENTS.md`](frontend/AGENTS.md) - Next.js patterns
