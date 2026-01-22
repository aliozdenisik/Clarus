# Active Context

## Current Work Focus

**Date**: 2026-01-22

**Removed Frontend** - Reverting to CLI/API specific architecture.

## Recent Changes

### Web Application Scaffold (2026-01-20)

**Backend (FastAPI)**:
- `app/main.py` - ASGI entrypoint with CORS
- `app/config.py` - Pydantic settings (JWT, OAuth, DB)
- `app/db.py` - SQLAlchemy async with PostgreSQL
- `app/models.py` - User, SearchHistory models
- `app/auth/` - JWT + Google OAuth authentication
- `app/api/` - auth, search, compare, stream routes


**Infrastructure**:
- `docker-compose.yml` - PostgreSQL + Qdrant
- `scripts/dev.sh` - Development startup script
- `WEB_APP_README.md` - Quick start guide

### Web App Search Filters (2026-01-21)

**Fronted**:
[REMOVED]


**Backend**:
- Updated `app/api/stream.py` to handle `ot`, `nt`, `apocrypha` source parameters.
- Updated `src/ultimate_rag.py` to support testament-specific `BibleSearcher` instantiation and caching.

### Tech Stack Decisions

| Layer | Technology |
|-------|------------|
| Backend | FastAPI + SQLAlchemy |
| Auth | JWT + Google OAuth |
| Database | PostgreSQL (Supabase Local) |
| Vector DB | Qdrant |

### Previous Work (Testament Collections)

| Collection | Points | Agent |
|------------|--------|-------|
| `quran_tr` | 6,236 | QuranAgent |
| `bible_ot` | 23,145 | OldTestamentAgent |
| `bible_nt` | 7,957 | NewTestamentAgent |
| `bible_apocrypha` | 5,717 | ApocryphaAgent |

## Next Steps

1. ✅ ~~Web Application Scaffold~~
2. **Backend API Hardening**
3. **CLI Feature Parity**
4. **Documentation Update**

## Active Decisions

- **Rate Limit**: 50 queries/day/user
- **Language**: Turkish
- **API First**: Focus on backend capabilities

## Learnings

1. **Vue 3 Composition API** works well with SSE streaming
2. **@vueuse/motion** provides lightweight animations
3. **FastAPI + SQLAlchemy async** handles concurrent requests efficiently
4. **Pinia** simplifies auth state management with localStorage persistence
