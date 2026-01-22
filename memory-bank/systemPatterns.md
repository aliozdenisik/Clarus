# System Patterns

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (API Only)                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────┐│
│  │  JWT Auth   │ │  API Routes │ │   SSE StreamingResponse     ││
│  │  + OAuth    │ │  (CRUD)     │ │   (Token-by-token)          ││
│  └─────────────┘ └─────────────┘ └─────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                    RAG Pipeline                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────┐│
│  │ UltimateRAG │ │Comparative  │ │  Multi-Agent Generator      ││
│  │ (Single)    │ │    RAG      │ │  (5 paragraphs)             ││
│  └─────────────┘ └─────────────┘ └─────────────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│                    Data Layer                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────────┐│
│  │ PostgreSQL  │ │   Qdrant    │ │        DiskCache            ││
│  │ (Users)     │ │ (Vectors)   │ │     (Embeddings)            ││
│  └─────────────┘ └─────────────┘ └─────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Design Principles

- **Scalability**: Async architecture supports concurrent users
- **Reliability**: Rate limiting prevents abuse
- **Maintainability**: Clean separation (frontend/backend/RAG)
- **Efficiency**: SSE streaming reduces perceived latency

## Key Technical Decisions

### 1. Vue 3 over React (MCDM)

- Lower learning curve
- Smaller bundle size (~18KB vs ~42KB)
- Efficient reactivity system
- Compatible with SSE via EventSource

### 2. FastAPI over Django/Flask

- Native async support (ASGI)
- Built-in OpenAPI docs
- Pydantic validation
- Easy SSE with StreamingResponse

### 3. JWT over Session Auth

- Stateless (no server-side session storage)
- Works with SPA architecture
- Easy Google OAuth integration

### 4. SSE over WebSocket

- Simpler for unidirectional streaming
- Native browser EventSource API
- Lower complexity for LLM token streaming

### 5. PostgreSQL via Docker

- User data persistence
- Search history tracking
- Rate limiting state

## Component Relationships

| Component | Dependencies | Purpose |
|-----------|--------------|---------|
| `frontend/` | Vue 3, Pinia, Tailwind | User interface |
| `app/main.py` | FastAPI, routers | API entrypoint |
| `app/auth/` | JWT, OAuth | Authentication |
| `app/api/` | RAG modules | API endpoints |
| `src/` | Qdrant, LLM APIs | RAG pipeline |

## API Flow

### Search with Streaming

1. Frontend sends query via fetch
2. Backend authenticates JWT
3. Rate limit check (50/day)
4. RAG pipeline executes search
5. SSE streams tokens to frontend
6. Frontend updates UI in real-time

### Authentication Flow

1. User submits credentials
2. Backend validates (bcrypt hash)
3. JWT token generated
4. Token stored in localStorage
5. Subsequent requests include Bearer token
