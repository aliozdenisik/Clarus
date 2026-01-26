# CLARUS - PROJECT KNOWLEDGE BASE

**Generated:** 2026-01-26
**Commit:** e0377c1
**Branch:** main

## OVERVIEW

Clarus is a maximum-accuracy RAG (Retrieval-Augmented Generation) search system for sacred texts (Quran in Turkish, Bible in English KJVA). Features 5-agent comparative theological analysis, semantic chunking, and hybrid search with RRF fusion.

## STRUCTURE

```
qdrant/                         # Root (project named after Qdrant DB it uses)
├── backend/                    # Python FastAPI + RAG pipeline
│   ├── main.py                 # CLI entrypoint (1364 lines - primary interface)
│   ├── app/                    # FastAPI REST API
│   │   ├── main.py             # ASGI server entrypoint
│   │   ├── api/                # Route handlers (8 files)
│   │   ├── auth/               # JWT + Google OAuth
│   │   ├── middleware/         # CORS, rate limiting
│   │   └── schemas/            # Pydantic models
│   ├── src/                    # RAG pipeline modules (17 files) ← CORE LOGIC
│   ├── tests/                  # Custom accuracy benchmarks (NOT pytest)
│   ├── scripts/                # Setup & dev scripts
│   └── data/                   # Source JSON (quran_tr.json, bible_kjva.json)
├── frontend/                   # Next.js 15 + Framer Motion
│   ├── app/                    # App Router pages
│   ├── components/             # UI components (Radix + custom)
│   ├── lib/                    # API client, hooks, stores
│   └── __tests__/              # Vitest + RTL tests
├── memory-bank/                # Project context (READ FIRST)
├── docker-compose.yml          # PostgreSQL + Qdrant services
└── qdrant_data/                # Qdrant persistent storage (43k vectors)
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add CLI command | `backend/main.py` | argparse + Rich formatting |
| Add API endpoint | `backend/app/api/` | FastAPI router pattern |
| Modify RAG pipeline | `backend/src/` | See `backend/src/AGENTS.md` |
| Add UI component | `frontend/components/` | Radix primitives + Framer Motion |
| Change auth flow | `backend/app/auth/` | JWT + OAuth handlers |
| Update API client | `frontend/lib/api/` | Generated via @hey-api/openapi-ts |
| Add test | `frontend/__tests__/` (Vitest) or `backend/tests/` (custom) |
| Project context | `memory-bank/` | Read `activeContext.md` first |

## CODE MAP

| Module | Location | Lines | Role |
|--------|----------|-------|------|
| `main.py` | backend/ | 1364 | CLI: search, ask, compare commands |
| `ultimate_rag.py` | backend/src/ | 593 | Core RAG: enhance → multi-query → search → fuse → answer |
| `comparative_rag.py` | backend/src/ | 776 | 4-collection parallel search + RRF fusion |
| `search.py` | backend/src/ | 974 | Qdrant hybrid search (dense+sparse) |
| `embeddings.py` | backend/src/ | 653 | OpenAI text-embedding-3-large + BM25 |
| `multi_agent_answer_generator.py` | backend/src/ | 530 | 5-agent system (Quran, OT, NT, Apocrypha, Summary) |
| `indexer.py` | backend/src/ | 722 | Qdrant collection management |
| `compare.py` | backend/app/api/ | 291 | Compare API + VerseDetail schema |
| `types.gen.ts` | frontend/lib/api/ | 1003 | Generated TypeScript API types |
| `compare/page.tsx` | frontend/app/ | 600+ | Multi-agent comparison UI + rich references |
| `source-badge.tsx` | frontend/components/compare/ | 30 | Colored source badge component |
| `source-reference-card.tsx` | frontend/components/compare/ | 74 | Verse card with badge + text |
| `filter-tabs.tsx` | frontend/components/compare/ | 45 | Filter tabs for source filtering |
| `inline-citation.tsx` | frontend/components/compare/ | 15 | Clickable inline citation |
| `parse-citations.ts` | frontend/lib/utils/ | 25 | Citation parsing utility |

## CONVENTIONS

### Python (backend/)
- **Imports**: Relative within `src/`, absolute for `app/`
- **Async**: All Qdrant/LLM calls are async
- **Error handling**: Explicit try-except with logging, no silent failures
- **Type hints**: Required on all function signatures

### TypeScript (frontend/)
- **Components**: Functional with explicit props interfaces
- **State**: Zustand stores in `lib/stores/`
- **API calls**: TanStack Query via generated client
- **Styling**: Tailwind + `cn()` utility from `lib/utils.ts`

### Naming
- Python: `snake_case` files, `PascalCase` classes
- TypeScript: `kebab-case` files, `PascalCase` components
- Collections: `quran_tr`, `bible_ot`, `bible_nt`, `bible_apocrypha`

## ANTI-PATTERNS (THIS PROJECT)

- **No `any` in TypeScript** - Types are generated from OpenAPI spec
- **No pytest** - Backend uses custom accuracy benchmark framework
- **No hardcoded API keys** - Must use `.env` file
- **No synchronous LLM calls** - Always async with timeout
- **Frontend is "zombie"** - Documentation says "removed" but code exists; confirm intent before modifying

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

### Testing Strategy
- **Frontend**: Standard Vitest + RTL (`npm test`)
- **Backend**: Custom `run_retrieval_accuracy_test.py` measuring F1 score against `test_data.json` ground truth

## COMMANDS

```bash
# Infrastructure
docker compose up -d                    # Start Qdrant + PostgreSQL

# Backend (from backend/)
source ../venv/bin/activate
python main.py search "sabir ve namaz"  # Quran search
python main.py ask "Islam'da sabir?"    # Q&A with citations
python main.py compare "Yaratilis"      # Multi-agent comparison
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

- **Rate limit**: 50 queries/day/user (configurable in `backend/app/config.py`)
- **Collections total**: 43,055 vectors (Quran 6,236 + Bible OT 23,145 + NT 7,957 + Apocrypha 5,717)
- **LLM costs**: ~$0.013/query with semantic cache (60-80% reduction)
- **Port conflicts**: Qdrant on 6333, PostgreSQL on 54322, API on 8000, Frontend on 3000
- **Memory bank**: Always read `memory-bank/activeContext.md` before starting work

## CHILD AGENTS.md

- [`backend/src/AGENTS.md`](backend/src/AGENTS.md) - RAG pipeline internals
- [`frontend/AGENTS.md`](frontend/AGENTS.md) - Next.js patterns
