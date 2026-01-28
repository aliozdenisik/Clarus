# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Clarus is a maximum-accuracy RAG (Retrieval-Augmented Generation) search system for sacred texts. It features 5-agent comparative theological analysis across Quran (Turkish) and Bible (English KJVA) with hybrid search using Reciprocal Rank Fusion (RRF).

**Key context files** - Read `memory-bank/activeContext.md` first before starting any work. The `memory-bank/` directory contains detailed project state and recent changes.

## Build & Run Commands

### Infrastructure
```bash
docker compose up -d                    # Start Qdrant + PostgreSQL
```

### Backend (from `backend/`)
```bash
source ../venv/bin/activate             # Activate virtualenv
uvicorn app.main:app --reload           # Start API server on :8000

# CLI commands
python main.py search "query"           # Quran search
python main.py search-bible "query"     # Bible search
python main.py ask "question"           # Q&A with citations
python main.py compare "topic"          # Multi-agent comparison
python main.py info                     # Collection stats
python main.py cache-clear              # Clear semantic cache
```

### Frontend (from `frontend/`)
```bash
npm install
npm run dev                             # Dev server on :3000
npm run build                           # Production build
npm test                                # Vitest + RTL
npm run lint                            # ESLint
```

### Full Stack
```bash
./start.sh                              # One-command startup
```

## Testing

**Backend**: Uses custom accuracy benchmarks, NOT pytest.
```bash
cd backend
python tests/run_retrieval_accuracy_test.py   # Ground-truth validation
python tests/run_e2e_benchmark.py             # End-to-end benchmark
python tests/test_circuit_breaker.py          # Resilience tests
python tests/test_health_endpoint.py          # Health check tests
```
Ground truth in `tests/test_data.json`. Target: 84%+ Quran F1, 75%+ Bible F1.

**Frontend**: Vitest + React Testing Library
```bash
cd frontend
npm test                                # Run all tests
npm test -- --run path/to/test.tsx      # Run single test
```

## Architecture

### 5-Agent Multi-Agent System
```
Query → [QuranAgent, OTAgent, NTAgent, ApocryphaAgent] → SummaryAgent → Essay
```
Each agent searches its collection and generates commentary. SummaryAgent synthesizes into 5-paragraph essay.

### Hybrid Search Pipeline
```
Query → LLM Enhancement → Multi-Query (3-5 variants) →
       Parallel Search (4 collections, dense+sparse) →
       RRF Fusion (k=60) → Answer Generation
```

### Key Collections
| Collection | Vectors | Agent |
|------------|---------|-------|
| `quran_tr` | 6,236 | QuranAgent |
| `bible_ot` | 23,145 | OldTestamentAgent |
| `bible_nt` | 7,957 | NewTestamentAgent |
| `bible_apocrypha` | 5,717 | ApocryphaAgent |

### Resilience Patterns
- **Circuit breakers** (`src/circuit_breaker.py`): qdrant_breaker, llm_breaker, embeddings_breaker
- **Retry with backoff**: Tenacity decorators on LLM calls (3 attempts, 2s→4s→8s)
- **Semantic cache** (`src/llm_cache.py`): 0.95 similarity threshold, 7-day TTL

## Code Conventions

### Python (backend/)
- All Qdrant/LLM calls must be async
- Type hints required on all function signatures
- Use `logging.getLogger(__name__)` not print
- Access collections via constants from `indexer.py`, not hardcoded strings
- Imports: relative within `src/`, absolute for `app/`

### TypeScript (frontend/)
- Functional components with explicit prop interfaces
- State management via Zustand stores in `lib/stores/`
- API calls via generated OpenAPI client in `lib/api/`
- Styling: Tailwind + `cn()` utility
- No `any` types (strict TypeScript)

### Naming
- Python: `snake_case` files, `PascalCase` classes
- TypeScript: `kebab-case` files, `PascalCase` components

## Key Files

| Task | Location |
|------|----------|
| CLI entrypoint | `backend/main.py` |
| API server | `backend/app/main.py` |
| RAG pipeline | `backend/src/ultimate_rag.py` |
| Comparative analysis | `backend/src/comparative_rag.py` |
| Multi-agent system | `backend/src/multi_agent_answer_generator.py` |
| Hybrid search | `backend/src/search.py` |
| Embeddings | `backend/src/embeddings.py` |
| API routes | `backend/app/api/` |
| Frontend pages | `frontend/app/` |
| UI components | `frontend/components/` |
| RAG docs | `backend/src/AGENTS.md` |

## Environment Variables

Required in `backend/.env`:
```env
OPENROUTER_API_KEY=sk-or-v1-...
```

Optional for API:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:54322/postgres
JWT_SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=...
SENTRY_DSN_BACKEND=...
```

## Port Configuration
- Backend API: 8000
- Frontend: 3000
- Qdrant: 6333
- PostgreSQL: 54322

## Anti-Patterns
- Never call LLM synchronously - always async with timeout
- Never hardcode collection names - use constants
- Never skip cache check before LLM calls
- No pytest in backend - use custom accuracy benchmarks
- Frontend noted as "zombified" in docs - confirm intent before major changes