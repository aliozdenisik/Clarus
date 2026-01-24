# System Patterns

## Architecture Overview

```
+-----------------------------------------------------------------------+
|                         User Interfaces                               |
|  +------------------+                    +---------------------------+|
|  |    CLI (Rich)    |                    |   REST API (FastAPI)      ||
|  |  python main.py  |                    |   uvicorn app.main:app    ||
|  +--------+---------+                    +-------------+-------------+|
|           |                                            |              |
+-----------+--------------------------------------------+--------------+
            |                                            |
            v                                            v
+-----------------------------------------------------------------------+
|                         RAG Pipeline                                  |
|  +---------------+  +---------------+  +-----------------------------+|
|  | UltimateRAG   |  | Comparative   |  |  Multi-Agent Generator      ||
|  | (Single Text) |  |     RAG       |  |  (5 paragraphs)             ||
|  +---------------+  +---------------+  +-----------------------------+|
+-----------------------------------------------------------------------+
            |
            v
+-----------------------------------------------------------------------+
|                         Data Layer                                    |
|  +---------------+  +---------------+  +-----------------------------+|
|  | PostgreSQL    |  |    Qdrant     |  |        DiskCache            ||
|  | (Users/Auth)  |  |  (Vectors)    |  |     (Embeddings)            ||
|  +---------------+  +---------------+  +-----------------------------+|
+-----------------------------------------------------------------------+
```

## Design Principles

- **CLI-First**: Primary interface is command-line for power users
- **API-Available**: REST API for programmatic access and integrations
- **Scalability**: Async architecture supports concurrent requests
- **Reliability**: Rate limiting prevents abuse (50/day/user)
- **Efficiency**: SSE streaming reduces perceived latency

## Key Technical Decisions

### 1. CLI as Primary Interface

- Direct access to all RAG features
- Rich formatting with tables and colors
- No authentication overhead for local use
- Fastest path from query to answer

### 2. FastAPI for REST API

- Native async support (ASGI)
- Built-in OpenAPI docs at `/docs`
- Pydantic validation
- Easy SSE with StreamingResponse

### 3. JWT over Session Auth

- Stateless (no server-side session storage)
- Works with any client (curl, Postman, custom apps)
- Easy Google OAuth integration

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
