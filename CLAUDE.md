# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**Clarus** is a maximum-accuracy RAG (Retrieval-Augmented Generation) search engine for sacred texts, featuring:
- Hybrid search (dense + sparse vectors) via Qdrant
- Multi-agent theological analysis (5 specialized LLM agents)
- Parallel search across 4 collections: Quran (Turkish), Bible OT/NT/Apocrypha (KJVA)
- **Citation deep linking** - Citations in AI answers directly open verse pages in new tabs
- FastAPI backend + Next.js 15 frontend
- 43,055 indexed verses with semantic chunking

**Stack**: Python 3.11+, FastAPI, Qdrant, OpenAI embeddings, OpenRouter LLMs, Next.js 15, PostgreSQL

---

## Quick Start (TL;DR)

```bash
# One-time setup (after cloning)
python3.11 -m venv venv && source venv/bin/activate
cd backend && pip install -r requirements.txt && cd ..
cp backend/.env.example backend/.env  # Edit and add OPENROUTER_API_KEY
python backend/scripts/setup_all_collections.py  # Requires Docker (starts automatically)

# Daily development
./start.sh  # Starts everything (Docker + Backend + Frontend)
```

**Access:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Qdrant Dashboard: http://localhost:6333/dashboard

---

## First-Time Setup

After cloning the repository, follow these steps in order:

### 1. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Note:** Python 3.11 or higher is required. Check with `python3.11 --version`.

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
cd ..
```

This installs all Python dependencies including Qdrant client, FastAPI, and ML libraries (~2-3 minutes).

### 3. Configure Environment Variables

```bash
# Backend (REQUIRED)
cp backend/.env.example backend/.env
# Edit backend/.env and set OPENROUTER_API_KEY (get from https://openrouter.ai/keys)

# Frontend (Optional - only needed for Google OAuth)
cp frontend/.env.example frontend/.env.local
# Edit frontend/.env.local and add NEXT_PUBLIC_GOOGLE_CLIENT_ID if using OAuth
```

**Required variables:**
- `OPENROUTER_API_KEY` - For LLM calls (OpenRouter provides access to multiple models)

**Optional variables:**
- Google OAuth credentials (for user authentication)
- Sentry DSNs (for error tracking)

### 4. Start Docker Services

```bash
docker compose up -d
```

This starts Qdrant (vector database) and PostgreSQL. Verify with:
```bash
curl http://localhost:6333/health  # Should return {"status":"ok"}
```

### 5. Index Collections (One-Time, ~2 minutes)

```bash
cd backend
source ../venv/bin/activate
python scripts/setup_all_collections.py
cd ..
```

This indexes 43,055 verses (Quran + Bible) into Qdrant with hybrid search vectors. Data files (`quran_tr.json`, `bible_kjva.json`) are included in the repository.

**Expected output:**
```
✓ quran_tr indexed (6,236 verses)
✓ bible_ot indexed (23,145 verses)
✓ bible_nt indexed (7,957 verses)
✓ bible_apocrypha indexed (5,717 verses)
```

### 6. Start Application

```bash
./start.sh
```

This runs backend API (port 8000) and frontend dev server (port 3000) with live reload.

**Troubleshooting:**
- **Port already in use:** `lsof -i :6333` (or :8000, :3000, :54322) and kill the process
- **Collections fail to index:** Ensure Docker is running with `docker compose ps`
- **Frontend fails to start:** Run `cd frontend && npm install`
- **venv activation fails:** Ensure Python 3.11+ is installed

---

## Development Commands

### Infrastructure

```bash
# Start/stop all services (Qdrant + PostgreSQL + Backend + Frontend)
./start.sh                    # One-command startup
./stop.sh                     # Graceful shutdown

# Docker only (Qdrant + PostgreSQL)
docker compose up -d          # Start infrastructure
docker compose down           # Stop infrastructure
```

### Backend (Python)

```bash
cd backend
source ../venv/bin/activate   # Activate virtual environment

# CLI Commands (Direct RAG pipeline access)
python main.py search "sabir ve namaz"              # Quran search
python main.py search-bible "love your neighbor"    # Bible search
python main.py ask "What is patience in Islam?"     # Q&A with citations
python main.py ask-bible "What is love?"            # Bible Q&A
python main.py compare "The concept of forgiveness" # Multi-agent comparison
python main.py compare --multi-agent "Creation"     # Detailed 5-agent essay
python main.py info                                 # Collection statistics
python main.py cache-info                           # Semantic cache stats
python main.py cache-clear                          # Clear LLM cache

# API Server
uvicorn app.main:app --reload                       # Dev server on :8000
uvicorn app.main:app --host 0.0.0.0 --port 8000     # Production

# One-time Setup (run after cloning)
python scripts/setup_all_collections.py             # Index all collections (~2 min)

# Testing
python tests/run_retrieval_accuracy_test.py         # RAG accuracy benchmark (F1 score)
python tests/run_e2e_benchmark.py                   # End-to-end latency test
python tests/test_circuit_breaker.py                # Resilience patterns test
pytest tests/                                       # Standard unit tests
```

### Frontend (Next.js)

```bash
cd frontend

# Development
npm install                   # Install dependencies
npm run dev                   # Dev server on :3000
npm run build                 # Production build
npm start                     # Production server

# Testing
npm test                      # Run Vitest tests
npm run lint                  # ESLint check

# Code Generation
npm run openapi-ts            # Regenerate TypeScript API client from OpenAPI spec
```

---

## Architecture

### High-Level Pipeline

```
Query → ENHANCE (LLM) → MULTI-QUERY (3-5 variants) → PARALLEL SEARCH (4 collections)
                                                    → RRF FUSION (k=60)
                                                    → MULTI-AGENT ANSWER (5 agents)
                                                    → ESSAY + CITATIONS
```

### Directory Structure

```
backend/
├── main.py                     # CLI entrypoint (1364 lines)
├── app/                        # FastAPI REST API
│   ├── main.py                 # ASGI server with lifespan, Sentry, CORS
│   ├── api/                    # Route handlers
│   │   ├── auth.py             # JWT + Google OAuth
│   │   ├── search.py           # Single-source search endpoints
│   │   ├── compare.py          # Multi-agent comparison endpoint
│   │   ├── stream.py           # SSE streaming responses
│   │   ├── admin.py            # User management
│   │   ├── metadata.py         # Collection metadata
│   │   └── preferences.py      # User preferences
│   ├── auth/                   # JWT token generation/validation
│   ├── middleware/             # Rate limiting, error handling
│   ├── schemas/                # Pydantic request/response models
│   ├── config.py               # Settings (via pydantic-settings)
│   ├── db.py                   # SQLAlchemy async setup
│   └── models.py               # Database models
├── src/                        # RAG Pipeline (17 modules)
│   ├── ultimate_rag.py         # Main pipeline orchestrator (593 lines)
│   ├── comparative_rag.py      # Cross-scripture search (776 lines)
│   ├── multi_agent_answer_generator.py  # 5-agent system (530 lines)
│   ├── answer_generator.py     # Single-source LLM answers
│   ├── comparative_answer_generator.py  # Essay generation
│   ├── search.py               # Qdrant hybrid search (974 lines)
│   ├── embeddings.py           # OpenAI + BM25 encoders (653 lines)
│   ├── indexer.py              # Collection management (722 lines)
│   ├── query_enhancer.py       # LLM query expansion
│   ├── llm_cache.py            # Semantic response caching (θ=0.95)
│   ├── semantic_chunker.py     # Quran verse grouping
│   ├── bible_semantic_chunker.py  # Bible verse grouping
│   ├── data_loader.py          # Quran JSON loader
│   ├── bible_loader.py         # Bible KJVA loader
│   ├── circuit_breaker.py      # Resilience (pybreaker)
│   ├── lemmatizer.py           # Turkish text normalization
│   └── turkish_utils.py        # Turkish-specific utilities
├── scripts/
│   ├── setup_all_collections.py  # One-time indexing script
│   ├── chaos_sentry_test.py      # Sentry integration test
│   └── test_sentry.py            # Sentry configuration test
├── tests/                      # Custom benchmarks (NOT pytest)
│   ├── run_retrieval_accuracy_test.py  # F1 score evaluation
│   ├── test_data.json          # Ground truth for accuracy tests
│   └── run_e2e_benchmark.py    # Latency benchmarks
├── data/
│   ├── quran_tr.json           # Quran Turkish translation (6,236 verses) [Included in repo]
│   └── bible_kjva.json         # Bible KJVA (36,819 verses) [Included in repo]
└── sentry/                     # Sentry dashboards & alert configs

frontend/
├── app/                        # Next.js App Router
│   ├── search/                 # Single-source search UI
│   ├── compare/                # Multi-agent comparison UI
│   └── layout.tsx              # Root layout with providers
├── components/                 # React components
│   ├── search/                 # Search-specific components
│   ├── compare/                # Comparison-specific components
│   │   ├── source-badge.tsx    # Colored source indicators
│   │   ├── source-reference-card.tsx  # Verse cards with badges
│   │   ├── filter-tabs.tsx     # Source filtering
│   │   └── inline-citation.tsx # Clickable citations
│   └── ui/                     # Radix UI primitives + custom
├── lib/
│   ├── api/                    # Generated TypeScript client (@hey-api/openapi-ts)
│   ├── stores/                 # Zustand state management
│   ├── hooks/                  # Custom React hooks
│   └── utils/                  # Utilities (cn, parseCitations)
└── __tests__/                  # Vitest + React Testing Library

memory-bank/                    # Project documentation
├── projectBrief.md             # Core requirements
├── productContext.md           # Product rationale
├── activeContext.md            # Current focus
├── systemPatterns.md           # Architecture patterns
├── techContext.md              # Tech stack details
└── progress.md                 # Status tracking
```

### 5-Agent System

The multi-agent answer generator creates comparative theological essays:

```python
# Agent Pipeline (multi_agent_answer_generator.py)
QuranAgent          → Searches quran_tr, generates Quranic perspective
OldTestamentAgent   → Searches bible_ot, Hebrew Bible perspective
NewTestamentAgent   → Searches bible_nt, Gospel perspective
ApocryphaAgent      → Searches bible_apocrypha, Deuterocanonical perspective
SummaryAgent        → Synthesizes 4 perspectives into 5-paragraph essay

# Output Structure
MultiAgentAnswer:
    topic: str
    commentaries: List[AgentCommentary]  # 4 agents (Quran, OT, NT, Apocrypha)
    summary: str                          # SummaryAgent synthesis
    citations: Dict[str, List[str]]       # Grouped by source
    confidence: float                     # Average confidence across agents
    to_essay() -> str                     # Full markdown essay
```

Each agent:
1. Receives user query
2. Searches its collection (hybrid search with RRF fusion)
3. Generates commentary with inline citations
4. Returns structured response with confidence score

---

## Key Patterns & Conventions

### Python (backend/)

**Async Everything**: All Qdrant and LLM calls are async. Use `async/await` consistently.

```python
# ✅ Correct
results = await client.query_points(...)
answer = await self._call_llm_async(...)

# ❌ Wrong
results = client.query_points(...)  # Blocks event loop
```

**Circuit Breaker Pattern**: Wrap external calls with circuit breakers to prevent cascading failures.

```python
from src.circuit_breaker import qdrant_with_breaker, llm_with_breaker

# ✅ CRITICAL: Use lambda to defer execution
results = qdrant_with_breaker(lambda: client.query_points(...))

# ❌ WRONG: Executes immediately, bypassing breaker
results = qdrant_with_breaker(client.query_points(...))
```

**Type Hints**: Required on all function signatures. No `Any` types.

```python
def search_quran(query: str, top_k: int = 10) -> List[UltimateSearchResult]:
    ...
```

**Error Handling**: Explicit try-except with logging. Never silent failures.

```python
try:
    results = await self._search(query)
except CircuitBreakerError:
    logger.error("Circuit breaker OPEN - service unavailable")
    raise  # Fail fast
except Exception as e:
    logger.error(f"Search failed: {e}")
    raise
```

**Logging**: Use `logging.getLogger(__name__)`, not `print()` or `console.print()` in library code.

**Collection Names**: Use constants from `indexer.py`, never hardcode strings.

```python
from src.indexer import QURAN_COLLECTION, BIBLE_OT_COLLECTION

# ✅ Correct
results = searcher.search(collection=QURAN_COLLECTION)

# ❌ Wrong
results = searcher.search(collection="quran_tr")
```

**LLM Cache**: Always check `SemanticCache` before making LLM calls (60-80% cost reduction).

```python
# Check cache first (θ=0.95 similarity threshold)
cached = self.llm_cache.get(query)
if cached:
    return cached

# Cache miss - call LLM and store result
response = await self._call_llm(query)
self.llm_cache.set(query, response)
return response
```

### TypeScript (frontend/)

**Component Structure**: Functional components with explicit props interfaces.

```typescript
interface SearchResultsProps {
  results: SearchResult[];
  isLoading: boolean;
}

export function SearchResults({ results, isLoading }: SearchResultsProps) {
  // ...
}
```

**API Calls**: Use TanStack Query with generated client from `lib/api/`.

```typescript
import { useQuery } from '@tanstack/react-query';
import { searchQuran } from '@/lib/api';

const { data, isLoading } = useQuery({
  queryKey: ['search', query],
  queryFn: () => searchQuran({ query })
});
```

**State Management**: Zustand stores in `lib/stores/` for global state.

```typescript
// lib/stores/searchStore.ts
import { create } from 'zustand';

interface SearchState {
  query: string;
  setQuery: (query: string) => void;
}

export const useSearchStore = create<SearchState>((set) => ({
  query: '',
  setQuery: (query) => set({ query })
}));
```

**Styling**: Tailwind CSS with `cn()` utility for merging classes.

```typescript
import { cn } from '@/lib/utils';

<div className={cn("base-class", isActive && "active-class")} />
```

**No `any` Types**: Use generated types from OpenAPI spec (`lib/api/types.gen.ts`).

**Citation Parsing & Display**: The `parseCitations()` utility automatically expands range and shorthand references.

```typescript
// frontend/lib/utils/parse-citations.ts
import { parseCitations } from '@/lib/utils/parse-citations';

// Input: "...ayetinde [Neml:2-4] anlatılır ve [Enfal:2, 9] belirtilir..."
// Output: [
//   "...ayetinde [",
//   { type: 'citation', reference: 'Neml:2' }, ", ",
//   { type: 'citation', reference: 'Neml:3' }, ", ",
//   { type: 'citation', reference: 'Neml:4' }, "] anlatılır ve [",
//   { type: 'citation', reference: 'Enfal:2' }, ", ",
//   { type: 'citation', reference: 'Enfal:9' }, "] belirtilir..."
// ]

// Expansion rules:
// - Range: "Neml:2-4" → ["Neml:2", "Neml:3", "Neml:4"]
// - Shorthand: "Enfal:2, 9" → ["Enfal:2", "Enfal:9"] (prepends surah name)
// - Multiple: "Bakara:1, 2, 3" → ["Bakara:1", "Bakara:2", "Bakara:3"]
```

**Why this matters**: Backend sends `verse_details` with individual verse keys (e.g., `"Neml:2"`, `"Neml:3"`), but LLMs naturally generate range citations (e.g., `"Neml:2-4"`). The frontend expansion bridges this gap, ensuring all citations are clickable and map to actual verse data.

**Citation Deep Linking** (✅ Implemented 2026-01-28): Citations in both search and compare systems are fully interactive. Clicking a citation opens the verse page in a new tab:
- Quran: `/quran/{surahId}?verse={verseId}` (e.g., `/quran/2?verse=153`)
- Bible: `/bible/{bookNr}?chapter={ch}&verse={v}` (e.g., `/bible/43?chapter=3&verse=16`)

The feature uses `verse_details` metadata from API responses, with graceful fallback to scroll behavior when metadata is unavailable. See `CITATION_DEEP_LINKING_FIX.md` for implementation details.

---

## RAG Pipeline Internals

### Search Flow

```
1. QueryEnhancer.enhance(query)
   └─> LLM expands query with synonyms, related concepts

2. Multi-Query Generation
   └─> Generate 3-5 query perspectives for better recall

3. Parallel Search (ThreadPoolExecutor)
   ├─> quran_tr (single verses)
   ├─> bible_ot (single verses)
   ├─> bible_nt (single verses)
   └─> bible_apocrypha (single verses)

4. RRF Fusion (k=60)
   └─> Combine results using Reciprocal Rank Fusion

5. AnswerGenerator / MultiAgentAnswerGenerator
   └─> LLM generates response with inline citations
```

### Hybrid Search Details

**Dense Vector**: OpenAI `text-embedding-3-large` (3072 dimensions)
**Sparse Vector**: Qdrant BM25 via FastEmbed
**Fusion**: Reciprocal Rank Fusion (RRF) with k=60

```python
# search.py implementation
def rrf_fusion(dense_results: List, sparse_results: List, k: int = 60) -> List:
    """
    RRF Score = Σ(1 / (k + rank_i))
    Combines dense and sparse results with equal weight
    """
    scores = defaultdict(float)
    for rank, result in enumerate(dense_results):
        scores[result.id] += 1.0 / (k + rank + 1)
    for rank, result in enumerate(sparse_results):
        scores[result.id] += 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

### Semantic Chunking

Groups consecutive verses into semantic chunks (2-7 verses) for better context retrieval.

**Quran**: `semantic_chunker.py` - Groups by topic coherence using sentence embeddings
**Bible**: `bible_semantic_chunker.py` - Similar approach for Bible verses

Collections:
- `quran_semantic_chunks` - Grouped Quran verses
- `bible_ot_chunks`, `bible_nt_chunks`, `bible_apocrypha_chunks` - Grouped Bible verses

---

## Configuration

### Environment Variables

#### Setting Up Environment Files

**Backend (REQUIRED):**
```bash
cp backend/.env.example backend/.env
```

Then edit `backend/.env` and set at minimum:
- `OPENROUTER_API_KEY` - Get from https://openrouter.ai/keys

**Frontend (Optional - only for Google OAuth):**
```bash
cp frontend/.env.example frontend/.env.local
```

Then edit `frontend/.env.local` if needed:
- `NEXT_PUBLIC_GOOGLE_CLIENT_ID` - Google OAuth client ID

#### Backend Environment Variables

**Required**:
- `OPENROUTER_API_KEY` - OpenRouter API key for LLM calls (multi-model access)

**Optional (with defaults)**:
- `DATABASE_URL` - PostgreSQL connection string (default: `postgresql+asyncpg://postgres:postgres@localhost:54322/postgres`)
- `JWT_SECRET_KEY` - JWT signing key (change in production, default provided for dev)
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` - Google OAuth credentials
- `RATE_LIMIT_PER_DAY` - Daily query limit per user (default: 50)
- `CORS_ORIGINS` - Comma-separated allowed origins (default: `http://localhost:3000`)
- `SENTRY_DSN_BACKEND` - Sentry DSN for error tracking

**Sentry (Optional)**:
- `SENTRY_DSN_BACKEND` - Backend error tracking
- `SENTRY_DSN_FRONTEND` - Frontend error tracking
- `SENTRY_ENVIRONMENT` - Environment name (development/production)
- `SENTRY_TRACES_SAMPLE_RATE` - Performance monitoring sample rate (0.0-1.0)

#### Frontend Environment Variables

**Optional**:
- `NEXT_PUBLIC_GOOGLE_CLIENT_ID` - Google OAuth client ID (public, safe for frontend)
- `NEXT_PUBLIC_SENTRY_DSN` - Sentry DSN for frontend error tracking
- `SENTRY_ORG` / `SENTRY_AUTH_TOKEN` - For source map uploads (CI/CD only)

### Settings Location

- Backend: `backend/app/config.py` (pydantic-settings)
- Frontend: `frontend/.env.local` (Next.js)
- Example files: `backend/.env.example`, `frontend/.env.example` (committed to git)

---

## Testing

### Backend Testing

**Two testing approaches:**

#### 1. Custom RAG Accuracy Benchmarks

These are NOT standard pytest tests - they evaluate RAG retrieval accuracy against ground truth:

```bash
# RAG accuracy test (measures F1 score against ground truth)
cd backend
python tests/run_retrieval_accuracy_test.py

# Output example:
# Quran Recall: 80%+
# Bible Recall: 100%
# Overall F1: 57%+
# Confidence: 96%

# End-to-end latency benchmark
python tests/run_e2e_benchmark.py

# Circuit breaker resilience test
python tests/test_circuit_breaker.py
```

Ground truth: `tests/test_data.json` - 30+ test queries with expected verse references.

#### 2. Standard Unit Tests (pytest)

```bash
cd backend
pytest tests/  # Runs standard unit tests with pytest
```

### Frontend Testing

```bash
# Unit tests (Vitest + React Testing Library)
npm test

# Component tests are in __tests__/
# Example: __tests__/components/SearchResults.test.tsx
```

---

## Common Tasks

### Add a New Search Feature

1. **Add method to `UltimateRAG`** (`backend/src/ultimate_rag.py`)
2. **Add API endpoint** (`backend/app/api/search.py`)
3. **Update frontend API client** (`npm run openapi-ts` in `frontend/`)
4. **Add UI component** (`frontend/components/search/`)

### Modify Embedding Strategy

1. **Edit `DenseEncoder`** in `backend/src/embeddings.py`
2. **Re-index collections** (`python scripts/setup_all_collections.py`)
3. **Update tests** (`tests/run_retrieval_accuracy_test.py`)

### Add New Agent to Multi-Agent System

1. **Create agent class** in `backend/src/multi_agent_answer_generator.py`
   ```python
   class NewAgent(BaseAgent):
       def __init__(self, rag: UltimateRAG):
           super().__init__(
               name="NewAgent",
               collection="new_collection",
               rag=rag
           )
   ```
2. **Add to agent list** in `MultiAgentAnswerGenerator.__init__()`
3. **Update `SummaryAgent` prompt** to include new perspective

### Modify RRF Fusion Parameters

1. **Edit `rrf_fusion()` in `backend/src/search.py`**
2. **Tune k-parameter** (default: 60)
3. **Run accuracy benchmark** to measure impact

### Add New Collection

1. **Prepare JSON data** (`backend/data/new_collection.json`)
2. **Create indexer method** in `backend/src/indexer.py`
3. **Add to setup script** (`backend/scripts/setup_all_collections.py`)
4. **Create searcher class** in `backend/src/search.py`
5. **Update `ultimate_rag.py`** to support new collection

---

## Resilience & Monitoring

### Circuit Breaker Configuration

Located in `backend/src/circuit_breaker.py`:

| Breaker | fail_max | reset_timeout | Purpose |
|---------|----------|---------------|---------|
| `qdrant_breaker` | 5 | 60s | Qdrant operations |
| `llm_breaker` | 3 | 30s | LLM API calls |
| `embeddings_breaker` | 10 | 120s | Batch embeddings |

**States**: CLOSED (normal) → OPEN (fast-fail) → HALF_OPEN (testing)

### Health Check Endpoint

```bash
curl http://localhost:8000/api/health
```

Returns:
```json
{
  "status": "healthy",  // or "degraded", "unhealthy"
  "version": "2.0.0",
  "event_loop": "ok",   // Detects blocking
  "qdrant": "connected" // Tests Qdrant connectivity
}
```

### Sentry Integration

**Backend**: Automatic error tracking with PII/LLM content redaction
**Frontend**: Performance monitoring + error tracking

Configuration: `backend/app/main.py` (lifespan function)

---

## Anti-Patterns

**Never**:
- Use `any` in TypeScript - types are generated from OpenAPI
- Call OpenAI synchronously - always use async client
- Skip LLM cache check - wastes money and time
- Hardcode collection names - use constants from `indexer.py`
- Use `print()` in library code - use `logging`
- Execute circuit breaker function immediately - wrap in lambda
- Return raw Qdrant response - wrap in domain objects
- Modify generated API client (`frontend/lib/api/`) manually - regenerate with `npm run openapi-ts`

**Frontend Status**: Active and maintained. Uses Next.js 15 App Router with full TypeScript coverage, TanStack Query for data fetching, and Zustand for state management.

---

## Performance & Cost

| Metric | Value | Notes |
|--------|-------|-------|
| Multi-Agent Latency | ~40s | 5 agents + summary generation |
| Single Search Latency | ~2-3s | Depends on collection size |
| Cost per Query | ~$0.013 | With semantic cache (60-80% reduction) |
| Cache Hit Rate | 60-80% | θ=0.95 similarity threshold |
| Collections | 43,055 vectors | Quran 6,236 + Bible 36,819 |
| Embedding Dimension | 3072 | OpenAI text-embedding-3-large |

---

## Port Reference

| Service | Port | Notes |
|---------|------|-------|
| Qdrant | 6333 | Vector database (HTTP) |
| Qdrant gRPC | 6334 | Vector database (gRPC) |
| PostgreSQL | 54322 | User data & auth |
| Backend API | 8000 | FastAPI server |
| Frontend | 3000 | Next.js dev server |

---

## Additional Resources

- **OpenAPI Docs**: http://localhost:8000/docs (when running)
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Backend RAG Details**: `backend/src/AGENTS.md`
- **Project Context**: `memory-bank/activeContext.md` (read before starting work)
- **Architecture**: `memory-bank/systemPatterns.md`
- **Sentry Configuration**: `backend/sentry/README.md`
- **Contributing**: `CONTRIBUTING.md`
