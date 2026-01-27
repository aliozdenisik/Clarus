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
│   └── lib/                # Utilities & API client
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
