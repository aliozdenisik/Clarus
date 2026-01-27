# Progress

## What Works

### Core Pipeline

- [x] Quran indexing and search (Turkish)
- [x] Bible indexing and search (KJVA English)
- [x] Hybrid search (Dense + Sparse)
- [x] Query enhancement with LLM
- [x] Embedding caching (DiskCache)
- [x] LLM Response Caching (Semantic cache)

### Advanced Features

- [x] Semantic chunking (Quran + Bible)
- [x] Multi-Query RAG with RRF fusion
- [x] Comparative RAG (4 parallel searches)
- [x] Multi-Agent Answer Generation (5 paragraphs)
- [x] Semantic LLM Cache (60-80% API cost reduction)

### Interfaces

- [x] CLI with Rich formatting
- [x] Python API for programmatic access
- [x] FastAPI backend with async SQLAlchemy
- [x] JWT + Google OAuth authentication
- [x] SSE streaming endpoints
- [x] Docker Compose (PostgreSQL + Qdrant)
- [x] Next.js 15 Frontend (Web App)

### Backend API

- [x] Circuit breaker protection (pybreaker)
- [x] Tenacity retry decorators on LLM calls
- [x] Enhanced health check (event_loop + Qdrant status)
- [x] Graceful shutdown in lifespan manager
- [x] SSE heartbeats (4 points in stream.py)
- [x] systemd service template and installer
- [x] CORS production configuration
- [x] Standardized error responses
- [x] Rate limit headers (X-RateLimit-*)
- [x] Token refresh mechanism
- [x] User preferences API
- [x] Metadata endpoints (collections, books, surahs)
- [x] Pagination for list endpoints
- [x] Input validation & XSS prevention
- [x] Compare API with rich response schema

### Frontend (Next.js 15)

- [x] SSE reconnection with exponential backoff
- [x] Auth timeout (10s) with offline detection
- [x] Offline banner component
- [x] backendStatus state in AuthContext
- [x] Landing page with animations
- [x] Login / Register pages
- [x] Search page (Kuran)
- [x] Apocrypha browse page
- [x] Compare page (Multi-agent analysis)
- [x] Linear-style dark theme
- [x] Framer Motion animations
- [x] GlowCard components
- [x] Navigation between pages
- [x] Rich source reference cards (verse details)
- [x] Filter tabs (by scripture source)
- [x] Clickable inline citations with scroll navigation
- [x] 2-second highlight animation on scroll target
- [x] Quran detail page (`/quran/[surahId]`) - Arapça ayetler + Türkçe meal
- [x] Bible detail page (`/bible/[bookNr]`) - Chapter seçimi + ayetler
- [x] Clean browse cards (removed `#nr` global numbering)
- [x] Arabic font support (Amiri - classic Naskh calligraphy)
- [x] Turkish translation display below Arabic verses

### CLI Commands

- [x] `setup` - Full indexing
- [x] `search` / `search-bible` - Basic search
- [x] `ask` / `ask-bible` - Q&A with citations
- [x] `compare` - Comparative analysis
- [x] `info` - Collection info
- [x] `cache-info` / `cache-clear` - Cache management

## Test Coverage Improvements (2026-01-27)

### New Frontend Test Files (Vitest + RTL)
| File | Tests | Coverage |
|------|-------|----------|
| `__tests__/use-sse.test.tsx` | 28 | SSE hook: reconnection, exponential backoff, state management |
| `__tests__/offline-banner.test.tsx` | 10 | Offline UI: render states, styling |
| `__tests__/compare-page.test.tsx` | 9 | Compare page: form, SSE streaming, filters |
| `__tests__/search-page.test.tsx` | 9 | Search page: input, results, loading states |
| `__tests__/auth-context.test.tsx` | +10 | Extended: timeout, backendStatus |

### New Backend Test Files (pytest)
| File | Tests | Coverage |
|------|-------|----------|
| `tests/test_circuit_breaker.py` | 39 | Circuit breakers: thresholds, wrappers, state transitions |
| `tests/test_health_endpoint.py` | 37 | Health API: response structure, status codes, Qdrant connectivity |

### Test Summary
- Frontend: 167 total tests (164 passing, 3 pre-existing failures)
- Backend: 76 unit tests (all passing)
- Total new tests added: 142

## What's Left to Build

### Frontend Enhancements

- [x] Bible search page (4-tab interface)
- [x] User preferences page
- [x] Search history page
- [x] SSE streaming integration
- [x] Browse pages (Quran, OT, NT, Apocrypha)
- [x] Global navigation
- [x] Vitest + RTL testing (71 tests)

### Production Deployment

- [ ] Google OAuth credentials setup
- [ ] Production Docker build
- [ ] HTTPS configuration
- [ ] Environment validation

### Potential Enhancements

- [x] Arabic font optimization (Amiri font + RTL support)
- [ ] Save/Share functionality
- [ ] Multi-language support
- [ ] Batch query API

## Current Status

| Area | Status | Notes |
|------|--------|-------|
| Core Search | Complete | 84%+ accuracy |
| Answer Generation | Complete | Gemini 2.5 Flash |
| Multi-Agent | Complete | 5-paragraph output |
| CLI | Complete | Rich formatting |
| REST API | Complete | FastAPI + JWT |
| Frontend | Complete | Next.js 15 + Framer Motion |
| Docker Setup | Complete | PostgreSQL + Qdrant |
| Browser Tests | Passed | Login ✅, Search ✅, Compare ✅ (rich refs) |

## Known Issues

1. **Port conflicts**: Ensure no existing Qdrant on 6333
2. **Google OAuth**: Requires credentials in .env
3. **Rate limiting**: 50/day per user (configurable)
4. **SSE 30s gap**: During multi-agent generation, no heartbeats (partial mitigation via reconnection)
5. **Circuit breaker silent degradation**: Returns empty results instead of error (intentional for UX)

## Evolution of Project

### Architecture Evolution

- **v1**: CLI-only Python application
- **v2**: Added multi-agent answer generation
- **v3**: Added FastAPI REST API
- **v3.1**: Removed Vue 3 frontend, CLI/API focus (current)

### Key Decisions

| Decision | Rationale |
|----------|-----------|
| Remove frontend | Simplify maintenance, CLI sufficient for use case |
| Keep REST API | Enables integrations and programmatic access |
| CLI as primary | Power users prefer command-line, no auth friction |
