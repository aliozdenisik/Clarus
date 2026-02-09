# System Patterns

## Architecture Overview

```
+-----------------------------------------------------------------------+
|                         User Interfaces                               |
|  +------------------+    +---------------------------+                |
|  |    Web App       |    |    CLI (Rich)             |                |
|  |  Next.js 15      |    |  python main.py           |                |
|  +--------+---------+    +---------+-----------------+                |
|           |                        |                                  |
|           v                        |                                  |
|  +---------------------------------+--------------------------+       |
|  |                    REST API (FastAPI)                      |       |
|  |                   uvicorn app.main:app                     |       |
|  +-----------------------------+------------------------------+       |
|                                |                                      |
|                                v                                      |
+-----------------------------------------------------------------------+
|                         RAG Pipeline                                  |
```

## Design Principles

- **Hybrid Interface**: CLI for dev/ops, Web App for end users
- **API-First**: All business logic exposed via REST API
- **Scalability**: Async architecture supports concurrent requests
- **Reliability**: Rate limiting prevents abuse (50/day/user)
- **Efficiency**: Semantic Caching & SSE streaming

## Key Technical Decisions

### 1. Next.js for Frontend

- **App Router**: Modern routing with server components
- **Framer Motion**: High-quality spring animations
- **Tailwind CSS**: Rapid styling with consistent design system
- **TypeScript**: Type safety across full stack

### 2. FastAPI for Backend

- **Native async support**: Handles concurrent RAG requests
- **Pydantic**: Shared schemas for API contracts
- **SSE**: Streaming responses for long-running agents

### 3. CLI for Power Users

- Direct access to RAG pipeline bypassing API overhead
- Rich formatting for debugging and analysis
- Immediate feedback loop for development

### 4. JWT Auth

- Stateless authentication for API scaling
- Refresh token rotation for security
- Unified auth for Web App and CLI (optional)

### 4. SSE over WebSocket

- Simpler for unidirectional streaming
- Native browser EventSource API
- Lower complexity for LLM token streaming

### 5. PostgreSQL for User Data

- User authentication persistence
- Search history tracking
- Rate limiting state

## Component Relationships

| Component | Dependencies | Purpose |
|-----------|--------------|---------|
| `main.py` | argparse, Rich, src/ | CLI entrypoint |
| `app/main.py` | FastAPI, routers | API entrypoint |
| `app/auth/` | JWT, OAuth | Authentication |
| `app/api/` | RAG modules | API endpoints |
| `src/` | Qdrant, LLM APIs | RAG pipeline |

## Frontend Performance Patterns

- **Batched tab indicator layout**: `frontend/components/ui/vercel-tabs.tsx` reads active/hover geometry and updates indicator state in one `useLayoutEffect` pass.
- **Virtualized long root lists**: `frontend/components/keyword-search/root-browser.tsx` uses `react-window` `List` for root browsing to avoid rendering all root rows at once.
- **Mousemove DOM-read caching**: `frontend/components/ui/magnetic-button.tsx` caches button bounds on `mouseenter` and reuses the cached rect during pointer movement.

## Data Flow

### CLI Search Flow

```
1. User runs: python main.py ask "question"
2. UltimateRAG enhances query with LLM
3. Multi-query expansion (3-5 perspectives)
4. Parallel search across 4 collections
5. RRF fusion combines results
6. LLM generates answer with citations
7. Rich formats and displays output
```

### API Search Flow

```
1. Client POSTs to /api/search/quran
2. JWT token validated
3. Rate limit checked (50/day)
4. RAG pipeline executes search
5. SSE streams tokens to client
6. Search saved to history (with result_count)
```

### Authentication Flow (API only)

```
1. User submits credentials to /api/auth/login
2. Backend validates (bcrypt hash)
3. JWT token generated (24h expiry)
4. Token returned to client
5. Subsequent requests include: Authorization: Bearer <token>
```

### SDK Client Auth Pattern

Frontend API calls use a globally configured SDK client that auto-injects auth tokens:

```
1. App initializes → configureApiClient() called in layout.tsx
2. client.setConfig({ auth: () => localStorage.getItem('access_token') })
3. SDK function called (e.g., getSearchHistory)
4. Client reads auth function → gets token
5. SDK prepends "Bearer " → Authorization header injected
6. Request sent with auth → Backend validates JWT
```

**Key Design Decisions:**
- Module-scope initialization (not React hook) — works in Server Components
- SSR-safe: `typeof window` check prevents server-side crashes
- No manual token handling in components — SDK auto-injects
- Auth token stored as `access_token` in localStorage (set by AuthContext)

### History Re-run Flow

When a user clicks a history card, the app navigates to the appropriate page with the query pre-filled:

```
History Card Click
      │
      ▼
getHistoryItemUrl(item)
      │
      ├── search_type matches "search_*" → /search?source={src}&q={query}
      ├── search_type matches "stream_search_*" → /search?source={src}&q={query}
      └── search_type matches "compare*" or "stream_compare" → /compare?q={query}
      │
      ▼
router.push(url)
      │
      ▼
Target Page Loads
      │
      ▼
useEffect reads `q` param from URL
      │
      ├── q is empty/absent → Do nothing
      └── q has value + hasAutoExecuted.current === false
            │
            ├── Set hasAutoExecuted.current = true
            ├── Set input value to q
            └── Call performBatchSearch(q) or performBatchCompare(q)
```

**Key Design Decisions:**
- `hasAutoExecuted` ref prevents infinite re-execution (not state — avoids re-render loops)
- `encodeURIComponent` on query for URL safety (special chars, Arabic text)
- `e.stopPropagation()` on delete button prevents navigation when deleting
- Compare page uses `Suspense` wrapper for `useSearchParams` (Next.js 15 requirement)

### React List Key Stability Pattern (Issue #94)

Frontend rendering follows stable-key rules to prevent reconciliation bugs and animation glitches:

```
Dynamic lists (results/citations/paragraphs)
  -> use data identity keys (reference/id/source composite)

Repeated primitive values (duplicate citations/words)
  -> use deterministic occurrence keys (value + occurrence counter)

Static placeholders (skeleton loaders)
  -> use deterministic prefixed keys (skeleton-context-index)
```

**Do:**
- Prefer domain IDs (`id`, `reference`, `source-reference`) for key identity.
- Use composite keys only when a single stable field is insufficient.
- Keep skeleton keys deterministic and namespaced by UI context.

**Don't:**
- Use direct index keys (`key={i}`, `key={index}`) in dynamic/reorderable lists.
- Use runtime-random keys (`Math.random`, timestamps) in render paths.

## Resilience Patterns

### Circuit Breaker (pybreaker)

Protects external service calls from cascading failures:

```
                    ┌─────────────┐
                    │   CLOSED    │ ← Normal operation
                    │  (passing)  │
                    └──────┬──────┘
                           │ fail_max failures
                           ▼
                    ┌─────────────┐
                    │    OPEN     │ ← Fast-fail, no calls
                    │  (blocking) │
                    └──────┬──────┘
                           │ reset_timeout
                           ▼
                    ┌─────────────┐
                    │  HALF_OPEN  │ ← Test single call
                    │  (testing)  │
                    └─────────────┘
```

| Breaker | fail_max | reset_timeout | Purpose |
|---------|----------|---------------|---------|
| `qdrant_breaker` | 5 | 60s | Database operations |
| `llm_breaker` | 3 | 30s | LLM API calls |
| `embeddings_breaker` | 10 | 120s | Batch embeddings |

**Usage Pattern (CRITICAL - use lambda):**
```python
from src.circuit_breaker import qdrant_with_breaker

# ✅ CORRECT
results = qdrant_with_breaker(lambda: client.query_points(...))

# ❌ WRONG - executes immediately
results = qdrant_with_breaker(client.query_points(...))
```

### Retry with Exponential Backoff (Tenacity)

Applied to all LLM calls:
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((Timeout, ConnectionError))
)
def _call_llm(self, ...):
    response = llm_with_breaker(lambda: requests.post(...))
```

**Key Design**: CircuitBreakerError is NOT retried (fail-fast when circuit open).

### SSE Connection Resilience

**Backend**: Heartbeats at 4 processing stages
```python
yield ": heartbeat\n\n"  # SSE comment format - invisible to EventSource
```

**Frontend**: Reconnection with exponential backoff
```typescript
const MAX_RETRIES = 3;
const delay = Math.pow(2, retryCount) * 1000;  // 1s, 2s, 4s
```

### Health Check Flow

```
GET /api/health
     │
     ├─► Event loop test (0.1s async sleep, 1s timeout)
     │   └─► blocked → status: "unhealthy"
     │
     ├─► Qdrant connectivity (2s timeout)
     │   └─► disconnected → status: "degraded"
     │
     └─► Response: {"status", "event_loop", "qdrant", "version"}
         └─► HTTP 200 (healthy) or 503 (degraded/unhealthy)
```

### Citation Architecture (Defense-in-Depth)

Three-layer defense against malformed LLM citations:

```
LLM Output → Backend Sanitizer → Frontend Parser → HoverCard Renderer
    │              │                    │                   │
    │         strip [[]]            require ':'         accent link
    │         trim spaces           expand ranges       verse preview
    │         normalize commas      expand commas       source badge
    │              │                    │                   │
    ▼              ▼                    ▼                   ▼
  Raw text    [X] format          CitationPart[]      Visual render
```

| Layer | File | Purpose |
|-------|------|---------|
| Sanitizer | `backend/src/citation_sanitizer.py` | Normalize `[[X]]` → `[X]`, trim, comma spacing |
| API Wiring | `backend/app/api/compare.py` | Apply sanitizer to all agent output |
| Parser | `frontend/lib/utils/parse-citations.ts` | Extract citations (colon-required), expand ranges |
| HoverCard | `frontend/components/compare/citation-hover-card.tsx` | Render as accent link with verse preview |
| InlineCitation | `frontend/components/compare/inline-citation.tsx` | Smart wrapper: HoverCard or muted fallback |

**Key Design Decisions:**
- Colon requirement (`:`): Distinguishes citations `[Bakara:45]` from non-citations `[sic]`
- No brackets in output: Parser returns `CitationPart[]` without `[` or `]` strings
- Idempotent sanitizer: Safe to apply multiple times
- Prompt + sanitizer: Defense-in-depth (prompts prevent, sanitizer catches)

### Morphological Keyword Search Architecture

Root-based deterministic search for Quran words, independent from the semantic RAG pipeline:

```
User Query (Arabic or Latin)
     │
     ▼
is_arabic() detection
     │
     ├── ARABIC PATH                    │ LATIN PATH
     │                                  │
     │ normalize_arabic()               │ normalize_latin_query()
     │ ↓                                │ ↓
     │ Step 1: token_clean exact match  │ Step L1: Buckwalter exact match
     │ ↓                                │ ↓
     │ Step 2: Prefix stripping         │ Step L2: pg_trgm fuzzy match
     │ (وال، ال، و، ف، ل، ب، ك)        │
     │ ↓                                │
     │ Step 3: Hamza-normalized root    │
     │ (SQL REPLACE أ/إ/آ → ا)          │
     │ ↓                                │
     │ Step 4: Tashaphyne algorithmic   │
     │                                  │
     └──────────────┬───────────────────┘
                    │
                    ▼
     PostgreSQL: qm_words → qm_ayahs → qm_surahs
                    │
                    ▼
     MorphologySearchResult (root, count, derived words, surah distribution, paginated verses)
```

| Component | File | Purpose |
|-----------|------|---------|
| Normalizer | `backend/src/arabic_normalizer.py` | Arabic/Latin text normalization |
| Search Service | `backend/src/quran_morphology.py` | Hybrid root extraction + DB queries |
| CLI | `backend/main.py` (`keyword-search`) | Rich terminal output |
| API Router | `backend/app/api/keyword_search.py` | 3 REST endpoints |
| Schemas | `backend/app/schemas/keyword_search.py` | Pydantic request/response models |
| ETL | `backend/scripts/setup_quran_morphology.py` | Tanzil XML + TSV → PostgreSQL |

**Key Design Decisions:**
- PostgreSQL deterministic (not semantic/vector) — 100% accuracy for root matching
- Independent from Qdrant collections — different data sources, different purposes
- Hamza normalization at query time (SQL REPLACE) — preserves original DB data
- Null byte sanitization — prevents PostgreSQL encoding crash
