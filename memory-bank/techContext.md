# Technical Context

## Technologies Used

| Category | Technology | Details |
|----------|------------|---------|
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

### URLs

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
| `/api/health` | GET | Health check |
| `/docs` | GET | OpenAPI documentation |
