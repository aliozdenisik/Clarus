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
6. Search saved to history
```

### Authentication Flow (API only)

```
1. User submits credentials to /api/auth/login
2. Backend validates (bcrypt hash)
3. JWT token generated (24h expiry)
4. Token returned to client
5. Subsequent requests include: Authorization: Bearer <token>
```
