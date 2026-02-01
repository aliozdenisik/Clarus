# Technical Context

## Technologies Used

| Category | Technology | Details |
|----------|------------|---------|
| **Frontend** | Next.js 15 | App Router, React 19, TypeScript |
| **Styling** | Tailwind CSS | Utility-first CSS, Radix UI primitives |
| **Animation** | Framer Motion | Spring animations, layout transitions |
| **Vector DB** | Qdrant | Docker, port 6333 |
| **Database** | PostgreSQL | Supabase Local, port 54322 |
| **Dense Embeddings** | OpenAI text-embedding-3-large | 3072 dim, via OpenRouter |
| **Sparse Embeddings** | Qdrant BM25 | FastEmbed |
| **LLM** | Gemini 2.5 Flash | Query enhancement + answers |
| **Backend** | FastAPI | Python 3.12, async |
| **Auth** | JWT + Google OAuth | python-jose, passlib |
| **CLI** | argparse + Rich | Primary Interface |
| **OS** | Ubuntu Linux | Docker native |

## Development Setup

### Prerequisites

```bash
# Start services (Qdrant + PostgreSQL)
docker compose up -d

# Python environment
source venv/bin/activate
pip install -r requirements.txt

# Node.js environment (Frontend)
cd frontend
npm install
npm run dev
```

### CLI Usage (Primary)

```bash
# Search
python main.py search "sabir ve namaz"
python main.py search-bible "love your neighbor"

# Q&A
python main.py ask "Islam'da sabir nedir?"
python main.py compare "Yaratilis hikayesi"
```

### API Usage (Optional)

```bash
# Start FastAPI server
uvicorn app.main:app --reload
```

### Environment Variables (.env)

```env
# Required
OPENROUTER_API_KEY=your-openrouter-key

# API Usage (optional)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:54322/postgres
JWT_SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
RATE_LIMIT_PER_DAY=50
```

## Sentry Observability

### Configuration

| Variable | Location | Description |
|----------|----------|-------------|
| `SENTRY_ENABLED` | Backend | Enable/disable Sentry (`true`/`false`) |
| `SENTRY_DSN_BACKEND` | Backend | Backend project DSN from Sentry |
| `SENTRY_ENVIRONMENT` | Backend | Environment tag (`development`/`production`) |
| `SENTRY_TRACES_SAMPLE_RATE` | Backend | Performance trace sampling (0.0-1.0) |
| `NEXT_PUBLIC_SENTRY_DSN` | Frontend | Frontend project DSN from Sentry |
| `SENTRY_ORG` | Frontend | Organization slug for source maps |
| `SENTRY_AUTH_TOKEN` | Frontend/CI | Auth token for source map upload |

### Backend Instrumentation

| Span Op | File | Description |
|---------|------|-------------|
| `llm.openrouter.query_enhancer` | query_enhancer.py | Query enhancement LLM calls |
| `llm.openrouter.answer` | answer_generator.py | Answer generation LLM calls |
| `llm.openrouter.comparative` | comparative_answer_generator.py | Comparative analysis LLM |
| `llm.openrouter.agent` | multi_agent_answer_generator.py | Multi-agent LLM calls |
| `embedding.openai.single` | embeddings.py | Single text embedding |
| `embedding.openai.batch` | embeddings.py | Batch embedding |
| `rag.enhance_query` | ultimate_rag.py | Query enhancement step |
| `rag.multi_query` | ultimate_rag.py | Multi-query generation |
| `rag.search` | ultimate_rag.py | Search with RRF fusion |

**Integrations**: SqlAlchemy (DB queries), FastAPI, Starlette

**Circuit Breaker Events**: Warning messages captured when breakers OPEN (qdrant, openrouter, embeddings)

### Frontend Instrumentation

- **Error Boundary**: Global React error capture with fallback UI (`components/error-boundary.tsx`)
- **SSE Capture**: Connection errors tracked with `source: 'sse-*'` tags
- **API Mutations**: Global error handler via QueryClient
- **User Context**: ID only (no PII - email/name scrubbed)

### Custom Metrics

| Metric | Unit | Description |
|--------|------|-------------|
| `rag.query.enhance_latency_ms` | millisecond | Query enhancement time |
| `rag.query.multi_latency_ms` | millisecond | Multi-query generation time |
| `rag.query.search_latency_ms` | millisecond | Search time |
| `rag.cache.hit` | none | Cache hit (1) or miss (0) |
| `rag.compare.total_latency_ms` | millisecond | Total compare time |
| `llm.tokens.input` | none | Input token count |
| `llm.tokens.output` | none | Output token count |
| `llm.cost.estimated` | none | Estimated cost in USD |

### PII Scrubbing (before_send hook)

- **Scrubbed**: user_email, user_name, email, name, user_id, llm_response, content, response, answer
- **Preserved**: Query text (for debugging), error messages

### Sampling Rate Tuning

| Environment | Rate | Use Case |
|-------------|------|----------|
| Development | `1.0` (100%) | Capture everything for debugging |
| Production (low traffic) | `0.1` (10%) | Balance visibility vs cost |
| Production (high traffic) | `0.01` (1%) | Reduce if performance impact |

### Alert Rules (Configure in Sentry UI)

| Alert | Condition | Level |
|-------|-----------|-------|
| Error Rate | >50 events/hour | Warning |
| Latency | p95 >60s on `rag.*` | Warning |
| Circuit Breaker | "Circuit breaker OPEN" event | Alert |
| LLM Error Rate | >20% on `llm.*` spans | Critical |

### Runbooks

See `backend/RUNBOOKS.md` for alert response procedures.

### Chaos Testing

```bash
cd backend
python scripts/chaos_sentry_test.py --all  # Test all alerts
python scripts/chaos_sentry_test.py --error-burst  # 100 errors
python scripts/chaos_sentry_test.py --slow-query   # 35s slow query
python scripts/chaos_sentry_test.py --circuit-open # Force breaker open
```

### Common False Positives (Already Filtered)

- EventSource reconnection errors (SSE retry behavior)
- ResizeObserver loop warnings (browser-specific)
- Network timeouts during development

### SSE Streaming Notes

- Compare endpoint streams take 40-60 seconds (normal)
- Transactions use `op: 'sse.stream'` to avoid "slow" marking
- Reconnection attempts are filtered (not sent to Sentry)

## URLs

| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Qdrant Dashboard | http://localhost:6333/dashboard |

## Dependencies

### Core (requirements.txt)

```
# Core RAG
qdrant-client>=1.7.0
fastembed>=0.2.0
rich>=13.0.0

# Resilience
pybreaker>=1.0.0
tenacity>=8.2.0

# REST API
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
sse-starlette>=2.0.0
pydantic-settings>=2.1.0
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
httpx>=0.26.0
```

## Directory Structure

```
qdrant/
├── main.py                 # CLI entrypoint (primary interface)
├── app/                    # FastAPI backend (REST API)
│   ├── main.py             # ASGI entrypoint
│   ├── config.py           # Pydantic settings
│   ├── db.py               # SQLAlchemy async
│   ├── models.py           # User, SearchHistory
│   ├── auth/               # JWT + OAuth
│   └── api/                # Route handlers
├── frontend/               # Next.js 15 Web App
│   ├── app/                # App Router pages
│   ├── components/         # UI Components
│   └── lib/                # Utilities, API client & auth config
├── src/                    # Python RAG modules
├── data/                   # Quran + Bible JSON
├── scripts/                # Setup scripts
├── docker-compose.yml      # PostgreSQL + Qdrant
└── memory-bank/            # Project documentation
```

## API Endpoints

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | User registration (returns access + refresh token) |
| `/api/auth/login` | POST | JWT login (returns access + refresh token) |
| `/api/auth/google` | POST | Google OAuth |
| `/api/auth/refresh` | POST | Refresh access token |
| `/api/auth/logout` | POST | Invalidate refresh token |
| `/api/auth/me` | GET | Get current user |
| `/api/auth/rate-limit` | GET | Get rate limit status |

### Search
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search/quran` | POST | Quran search (validated, paginated) |
| `/api/search/bible` | POST | Bible search (validated, paginated) |
| `/api/search/history` | GET | Search history (paginated) |
| `/api/search/history/{id}` | DELETE | Delete history item |
| `/api/search/history` | DELETE | Clear all history |
| `/api/stream/search` | GET | SSE streaming search |
| `/api/stream/compare` | GET | SSE streaming compare |

### Compare & Metadata
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/compare/` | POST | Multi-agent comparison |
| `/api/metadata/collections` | GET | Qdrant collections info |
| `/api/metadata/quran/surahs` | GET | All surahs list |
| `/api/metadata/quran/surahs/{id}` | GET | Surah detail with verses |
| `/api/metadata/bible/books` | GET | All books list (filter by testament) |
| `/api/metadata/bible/books/{nr}` | GET | Book detail with chapters |
| `/api/metadata/testaments` | GET | Testament list |

### Keyword Search (Morphological)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search/keyword/` | POST | Root-based keyword search (Arabic or Buckwalter Latin input) |
| `/api/search/keyword/roots` | GET | List all 1,651 Arabic roots with occurrence counts (paginated) |
| `/api/search/keyword/root/{root}` | GET | Get info for a specific root |

### Preferences & Admin
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/preferences/` | GET/PUT/DELETE | User preferences CRUD |
| `/api/admin/stats` | GET | Dashboard statistics |
| `/api/admin/users` | GET | User list (paginated) |
| `/api/admin/system` | GET | System info |
| `/api/config` | GET | Public config (rate limits, etc) |
| `/api/health` | GET | Health check (event_loop, qdrant connectivity, status) |
| `/docs` | GET | OpenAPI documentation |

## Resilience Infrastructure

### systemd Service

Install script and template at `backend/scripts/`:

```bash
# Install service
./backend/scripts/systemd-install.sh /path/to/backend /path/to/venv

# Service management
sudo systemctl enable --now clarus-backend
sudo systemctl status clarus-backend
journalctl -u clarus-backend -f
```

### Health Check Response

```json
{
  "status": "healthy",     // healthy | degraded | unhealthy
  "version": "2.0.0",
  "event_loop": "ok",      // ok | blocked
  "qdrant": "connected"    // connected | disconnected
}
```
- HTTP 200: healthy
- HTTP 503: degraded or unhealthy

## Logging Architecture

The Clarus logging system provides structured, correlation-enabled logging across frontend and backend with Sentry integration.

**Documentation:**
- Backend: `backend/LOGGING.md`
- Frontend: `frontend/LOGGING.md`

### Structured Logging Fields

| Field | Source | Description |
|-------|--------|-------------|
| `timestamp` | Auto | ISO 8601 UTC timestamp |
| `level` | Auto | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `logger` | Auto | Module/component name |
| `message` | Code | Log message |
| `request_id` | Middleware | Unique per HTTP request (8 chars) |
| `correlation_id` | Client | UUID tracking user action across services |
| `user_id` | Auth | Authenticated user ID |

### Correlation ID Flow

```
[Frontend]                    [Backend]                     [Logs]
    │                             │                            │
    │ User clicks "Search"        │                            │
    │ Generate UUID               │                            │
    ├─────────────────────────────┤                            │
    │ X-Correlation-ID: abc123    │                            │
    │ POST /api/search            │                            │
    │                             ├────────────────────────────┤
    │                             │ correlation_id=abc123      │
    │                             │ request_id=def456          │
    │                             │ INFO: Search started       │
    │                             │                            │
    │                             ├────────────────────────────┤
    │                             │ correlation_id=abc123      │
    │                             │ INFO: Qdrant query         │
    │                             │                            │
    │ Response                    │                            │
    │ X-Correlation-ID: abc123    │                            │
    │ X-Request-ID: def456        │                            │
    ├─────────────────────────────┤                            │
    │ Log: Search completed       │                            │
    │ correlation_id=abc123       │                            │
```

**Tracing a user action:**
```bash
# Find all logs for a single user action
grep "correlation_id.*abc123" /var/log/clarus/backend.log

# Backend (JSON format)
jq 'select(.correlation_id == "abc123")' backend.log
```

### Backend Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Minimum log level |
| `LOG_FORMAT` | `console` | `console` (dev) or `json` (prod) |
| `LOG_FILE` | None | Optional file path (rotates at 10MB) |

### Frontend Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_LOG_LEVEL` | `info` | Minimum log level (`debug`, `info`, `warn`, `error`) |

### Key Files

| File | Purpose |
|------|---------|
| `backend/app/logging_config.py` | Python logging setup, formatters, context injection |
| `backend/app/middleware/correlation.py` | Request/correlation ID middleware |
| `frontend/lib/logger.ts` | TypeScript logger service with Sentry integration |

### Output Formats

**Console (Development):**
```
[2024-01-15 10:30:00] INFO  app.api.search - Search completed [req=abc12345, user=42, latency_ms=150.25]
```

**JSON (Production):**
```json
{"timestamp":"2024-01-15T10:30:00.123Z","level":"INFO","logger":"app.api.search","message":"Search completed","request_id":"abc12345","user_id":42,"latency_ms":150.25}
```

### Sentry Integration

- **Backend**: Errors logged with `exc_info=True` captured automatically
- **Frontend**: `logger.error()` with Error object captured via Sentry SDK
- **Breadcrumbs**: Warnings create Sentry breadcrumbs for debugging context
- **Tags**: `component`, `action`, `correlationId` added to Sentry events

## SDK Client Auth Pattern

The frontend uses `@hey-api/openapi-ts` generated SDK client with global auth configuration.

**Configuration File:** `frontend/lib/api/config.ts`

```typescript
import { client } from './client.gen';

export function configureApiClient() {
  client.setConfig({
    auth: () => {
      if (typeof window === 'undefined') return undefined;
      return localStorage.getItem('access_token') || undefined;
    },
  });
}
```

**Initialization:** Called at module scope in `frontend/app/layout.tsx`:
```typescript
import { configureApiClient } from "@/lib/api/config";
configureApiClient();
```

**How it works:**
1. SDK functions define `security: [{scheme: 'bearer', type: 'http'}]`
2. Client calls the auth function before each request
3. Function reads `access_token` from localStorage (browser-only)
4. SDK prepends `Bearer ` automatically → `Authorization: Bearer <token>`
5. SSR-safe: Returns `undefined` on server (no localStorage)

**Usage:** SDK functions auto-inject auth — no manual headers needed:
```typescript
// Auth is automatic — just call the function
const response = await getSearchHistoryApiSearchHistoryGet({ query: { page: 1, limit: 20 } });
```

## Multilingual Query Translation

### Architecture

```
User Query (any language) → QueryTranslator → Translated Query (corpus language) → RAG Pipeline → Answer → Response Translation → User Language
```

### Translation Flow

| Step | Component | What Happens |
|------|-----------|-------------|
| 1. Heuristic Check | `QueryTranslator._heuristic_detect()` | Turkish chars + quran → skip LLM; ASCII + bible → skip LLM |
| 2. LLM Detection + Translation | `QueryTranslator._call_llm_json()` | Single call via `google/gemini-2.5-flash-lite` |
| 3. Search | `UltimateRAG` / `ComparativeRAG` | Uses translated query in corpus language |
| 4. Response Translation | `QueryTranslator.translate_response()` | Translates answer back to user's language |

### Supported Languages

| Code | Language | Role |
|------|----------|------|
| `tr` | Turkish | Native for Quran corpus |
| `en` | English | Native for Bible corpus |
| `es` | Spanish | Translated |
| `fr` | French | Translated |
| `it` | Italian | Translated |
| `pt` | Portuguese | Translated |
| `ar` | Arabic | Translated |
| `de` | German | Translated |

### Key Files

| File | Purpose |
|------|---------|
| `backend/src/query_translator.py` | Core translation module (614 lines) |
| `backend/tests/test_query_translator.py` | Unit tests (15 tests, mocked LLM) |
| `backend/tests/test_translation_accuracy.py` | Accuracy tests (40 pairs, 8 languages) |
| `frontend/components/search/language-selector.tsx` | Language dropdown UI (Radix) |

### API Changes

| Endpoint | New Request Field | New Response Field |
|----------|------------------|-------------------|
| `POST /api/search/quran` | `language: Optional[str]` | `detected_language: Optional[str]` |
| `POST /api/search/bible` | `language: Optional[str]` | `detected_language: Optional[str]` |
| `POST /api/compare/` | `language: Optional[str]` | `detected_language`, `response_language` |
| `GET /api/stream/search` | `language` query param | (in SSE events) |
| `GET /api/stream/compare` | `language` query param | (in SSE events) |

### Cost Impact

- Translation adds ~$0.003/query (~20% increase)
- Zero overhead for native queries (heuristic pre-filter skips LLM)
- Cross-lingual cache: Turkish cache hit serves English user after response translation

### Known Limitations

- German `ö`/`ü` are in `TURKISH_CHARS` set → German queries with those chars + quran corpus trigger Turkish heuristic (false positive)
- Pure ASCII foreign text (e.g., "amor en la Biblia") + bible corpus triggers English heuristic (false positive)
- These are acceptable tradeoffs — search still works, just not translated

## SearchHistory Model

The `SearchHistory` model tracks all user search and compare operations.

**Table:** `search_history`

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INTEGER | NOT NULL | Primary key |
| `user_id` | INTEGER | NOT NULL | FK → users.id |
| `query` | TEXT | NOT NULL | Search query text |
| `search_type` | VARCHAR(50) | NOT NULL | Operation type (13 values) |
| `created_at` | TIMESTAMP | NOT NULL | UTC timestamp |
| `result_count` | INTEGER | NULL | Result count (null for streaming) |

**13 search_type values:**

| Value | Source | Label |
|-------|--------|-------|
| `search_quran` | search.py | Quran |
| `search_bible_all` | search.py | Bible |
| `search_bible_ot` | search.py | Old Testament |
| `search_bible_nt` | search.py | New Testament |
| `search_bible_apocrypha` | search.py | Apocrypha |
| `stream_search_quran` | stream.py | Quran |
| `stream_search_bible` | stream.py | Bible |
| `stream_search_ot` | stream.py | Old Testament |
| `stream_search_nt` | stream.py | New Testament |
| `stream_search_apocrypha` | stream.py | Apocrypha |
| `compare_multi_agent` | compare.py | Multi-Agent |
| `compare` | compare.py | Compare |
| `stream_compare` | stream.py | Compare |

## Quran Morphology Database

### Schema (3 PostgreSQL Tables)

| Table | Rows | Purpose |
|-------|------|---------|
| `qm_surahs` | 114 | Surah metadata (name_arabic, name_translit, name_english, revelation_type) |
| `qm_ayahs` | 6,236 | Verse text (text_uthmani for display, text_clean for search) |
| `qm_words` | 77,429 | Morphological word data (token, root, lemma, pos_tag, features) |

### Key Columns (`qm_words`)

| Column | Type | Purpose |
|--------|------|---------|
| `token` | VARCHAR(100) | Original form with diacritics (display) |
| `token_clean` | VARCHAR(100) | Normalized form without diacritics (search) |
| `root` | VARCHAR(20) | Arabic root (e.g., كتب) — nullable for particles |
| `root_buckwalter` | VARCHAR(20) | Buckwalter Latin transliteration (e.g., ktb) |
| `lemma` | VARCHAR(50) | Lemma/dictionary form |
| `pos_tag` | VARCHAR(20) | Part of speech tag (N, V, P, etc.) |

### Indexes

| Index | Type | Column |
|-------|------|--------|
| `ix_qm_words_root` | B-Tree | root (exact match) |
| `ix_qm_words_root_bw` | B-Tree | root_buckwalter (exact match) |
| `ix_qm_words_root_bw_trgm` | GIN | root_buckwalter (fuzzy pg_trgm) |
| `ix_qm_words_token_clean_trgm` | GIN | token_clean (fuzzy pg_trgm) |

### Root Extraction Pipeline

```
User Input → is_arabic()?
├── Arabic Path: normalize → token_clean exact → prefix strip → hamza-normalized root match → Tashaphyne fallback
└── Latin Path: normalize → Buckwalter exact → pg_trgm fuzzy match
```

### Arabic Normalization (`arabic_normalizer.py`)
- Strip tashkeel (diacritics)
- Hamza: أ/إ/آ → ا, ؤ → و, ئ → ي
- Ta-marbuta: ة → ه
- Alef-maksura: ى → ي
- Strip tatweel (ـ)
- NFC Unicode normalization

### Dependencies
- `tashaphyne` — Arabic light stemmer (algorithmic fallback)
- `pyarabic` — Arabic text normalization + Buckwalter transliteration
- `psycopg2-binary` — PostgreSQL sync driver (for ETL scripts)

