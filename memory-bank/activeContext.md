# Active Context

## Current Work Focus

**Date**: 2026-01-20

**Web Application Implementation** - CLI converted to full-stack web app with Vue 3 + FastAPI.

## Recent Changes

### Web Application Scaffold (2026-01-20)

**Backend (FastAPI)**:
- `app/main.py` - ASGI entrypoint with CORS
- `app/config.py` - Pydantic settings (JWT, OAuth, DB)
- `app/db.py` - SQLAlchemy async with PostgreSQL
- `app/models.py` - User, SearchHistory models
- `app/auth/` - JWT + Google OAuth authentication
- `app/api/` - auth, search, compare, stream routes

**Frontend (Vue 3)**:
- Vue 3 + Vite + Tailwind CSS + Pinia
- 6 views: Home, Login, Register, Search, Results, Compare
- SSE streaming composable for real-time LLM responses
- Design system from konsept-frontend (Inter font, Material icons)

**Infrastructure**:
- `docker-compose.yml` - PostgreSQL + Qdrant
- `scripts/dev.sh` - Development startup script
- `WEB_APP_README.md` - Quick start guide

### Tech Stack Decisions

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3 + Vite + Tailwind |
| State | Pinia |
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
2. **Test full auth flow** - Register, Login, JWT
3. **SSE Streaming** - Verify token-by-token display
4. **Google OAuth** - Add credentials to .env
5. **Production build** - Frontend optimization

## Active Decisions

- **Rate Limit**: 50 queries/day/user
- **Language**: Turkish UI only
- **Theme**: Light default, dark mode toggle
- **Responsive**: Desktop-first
- **MVP Exclusions**: Save/Share, Arabic font optimization

## Learnings

1. **Vue 3 Composition API** works well with SSE streaming
2. **@vueuse/motion** provides lightweight animations
3. **FastAPI + SQLAlchemy async** handles concurrent requests efficiently
4. **Pinia** simplifies auth state management with localStorage persistence
