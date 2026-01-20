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
| **Frontend** | Vue 3 + Vite | Tailwind CSS, Pinia |
| **Auth** | JWT + Google OAuth | python-jose, passlib |
| **CLI** | argparse + Rich | Still available |
| **OS** | Ubuntu Linux | Docker native |

## Development Setup

### Prerequisites

```bash
# Start all services
docker compose up -d

# Backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Environment Variables (.env)

```env
# Existing
OPENROUTER_API_KEY=your-openrouter-key

# Web Application
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:54322/postgres
JWT_SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
RATE_LIMIT_PER_DAY=50
```

### URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Qdrant | http://localhost:6333/dashboard |

## Dependencies

### Backend (requirements.txt)

```
# Core
qdrant-client>=1.7.0
fastembed>=0.2.0
rich>=13.0.0

# Web Application
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

### Frontend (package.json)

```json
{
  "dependencies": {
    "vue": "^3.5.24",
    "vue-router": "^4.5.1",
    "pinia": "^3.0.3",
    "@vueuse/core": "^13.2.0",
    "@vueuse/motion": "^3.0.3"
  },
  "devDependencies": {
    "vite": "^7.2.4",
    "tailwindcss": "^3.4.0"
  }
}
```

## Directory Structure

```
qdrant/
├── main.py                 # CLI entrypoint
├── app/                    # [NEW] FastAPI backend
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── auth/
│   └── api/
├── frontend/               # [NEW] Vue 3 SPA
│   ├── src/
│   │   ├── views/
│   │   ├── components/
│   │   ├── stores/
│   │   └── composables/
│   └── package.json
├── src/                    # Python RAG modules
├── docker-compose.yml      # PostgreSQL + Qdrant
├── scripts/dev.sh          # Development startup
└── memory-bank/            # Documentation
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | User registration |
| `/api/auth/login` | POST | JWT login |
| `/api/auth/google` | POST | Google OAuth |
| `/api/search/quran` | POST | Quran search |
| `/api/search/bible` | POST | Bible search |
| `/api/stream/search` | GET | SSE streaming search |
| `/api/compare/` | POST | Multi-agent comparison |
