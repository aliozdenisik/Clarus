# Progress

## What Works

### Core Pipeline

- [x] Quran indexing and search (Turkish)
- [x] Bible indexing and search (KJVA English)
- [x] Hybrid search (Dense + Sparse)
- [x] Query enhancement with LLM
- [x] Embedding caching (Redis Stack 7.2)
- [x] LLM Response Caching (Semantic cache)
- [x] Multi-translator Quran indexing (8 Turkish translations from Tanzil XML)
- [x] Turkish Bible indexing (OT + NT from OSIS XML)

### Advanced Features

- [x] Semantic chunking (Quran + Bible)
- [x] Multi-Query RAG with RRF fusion
- [x] Comparative RAG (4 parallel searches)
- [x] Multi-Agent Answer Generation (5 paragraphs)
- [x] Semantic LLM Cache (60-80% API cost reduction)
- [x] Sentry Observability Documentation (Backend & Frontend)
- [x] Confidence Scoring Documentation (`docs/CONFIDENCE_SCORING.md`)

### Interfaces

- [x] CLI with Rich formatting
- [x] Python API for programmatic access
- [x] FastAPI backend with async SQLAlchemy
- [x] Better Auth (JWT plugin + JWKS bridge) — replaced custom JWT + Google OAuth
- [x] SSE streaming endpoints
- [x] Docker Compose (PostgreSQL + Qdrant + Redis)
- [x] Next.js 15 Frontend (Web App)

### Backend API

- [x] SearchHistory `result_count` column + migration script
- [x] History API `result_count` in response items
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
- [x] **SSE streaming format fix** (structured paragraphs + stats)
- [x] Citation sanitizer for LLM output normalization
- [x] Strengthened LLM prompts against double-bracket drift
- [x] **Confidence Scoring 2.0**: Two-phase sigmoid calibration (40-95% range)
- [x] Quran morphological keyword search API (`/api/search/keyword`) — root-based search, root listing, root info
- [x] Quran morphological keyword search — hamza normalization fix (137 roots, 10K+ words)
- [x] Null byte input sanitization (HTTP 500 → graceful 200)
- [x] 48-vector security test suite passed (SQL injection, XSS, command injection, DoS, Unicode)
- [x] Better Auth integration — JWKS validator, API key auth, user migration script

### Frontend (Next.js 15)

- [x] Search history page — SDK client migration, result_count display, search_type mapping
- [x] SDK client global auth (`lib/api/config.ts` — auto-injects Bearer token)
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
- [x] Landing page redesign — utilitarian luxury (Linear/Vercel standard), non-technical audience
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
- [x] History re-run search (RFC-001) — clickable history cards, auto-search/compare via URL params
- [x] Pre-existing test fixes — score assertion + removed obsolete logout test
- [x] Citation system overhaul — defense-in-depth: backend sanitizer + rewritten parser + Radix HoverCard (Issue #16)
- [x] HoverCard verse preview on citation hover
- [x] 35 citation parser unit tests (comprehensive coverage)
- [x] SSE stats parsing fix — aligned with backend message format (Issue #17)
- [x] Search navigation — 4-collection dropdown matching search page tabs (Issue #18)
- [x] Apocrypha book count in navigation menu (Issue #19)
- [x] Compare page UI alignment — matched search page design standards (Issue #20)
- [x] Keyword search frontend (RFC-007) — `/keyword-search` page with 8 components, Recharts chart, root browser, 26 tests
- [x] Keyword search QA fixes — Latin transliteration for surah names, API response nesting fix
- [x] Bible keyword search frontend — Word Search page with Hebrew/Greek tabs, Latin transliteration support
- [x] **Hebrew Latin transliteration fix** (2026-02-04): dot-separated syllabification normalization (`e.lo.him` → `elohim`)
- [x] **Bible keyword search fixes** (2026-02-04): Hebrew b↔v dual-indexing, occurrence-based prioritization, Greek Strong's preservation
- [x] **Bible keyword search verification** (2026-02-04): Validated against Blue Letter Bible — all discrepancies <1% (acceptable text tradition variance)
- [x] **Accuracy disclaimer UI** (2026-02-04): Added expandable accuracy verification panel to Bible Word Search with "Clarus can make mistakes" disclaimer, BLB comparison table, data source info (8 tests)
- [x] Better Auth UI — sign-in/sign-up pages, session management via useSession()
- [x] **Issue #94 React key stability** (2026-02-09): Replaced index-based keys in dynamic lists and standardized deterministic skeleton keys across search/compare/history/browse/components
- [x] **Issue #92 SSE pass optimization** (2026-02-09): Replaced multi-pass `filter().map()` chains and repeated `find()` scans in search/compare streaming handlers with single-pass reducers and one-loop source counters

### CLI Commands

- [x] `setup` - Full indexing
- [x] `search` / `search-bible` - Basic search
- [x] `ask` / `ask-bible` - Q&A with citations
- [x] `compare` - Comparative analysis
- [x] `info` - Collection info
- [x] `cache-info` / `cache-clear` - Cache management
- [x] `keyword-search` - Morphological root-based Quran keyword search (Arabic + Buckwalter Latin)
- [x] `search --translator` - Multi-translator Quran search
- [x] `index-quran` / `index-bible-tr` - Turkish collection indexing

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

### Playwright E2E Tests (2026-01-28)
| File | Tests | Coverage |
|------|-------|----------|
| `e2e/compare.spec.ts` | 2 | Compare page: auth, 5 paragraphs, stats, verse cards, filters, citations |

### Test Summary
- Frontend: 178 total tests (12 new for history re-run, 2 pre-existing fixes)
- Frontend E2E: 2 Playwright tests (core functionality verified ✅, timing issues to fix)
- Backend: 76 unit tests (all passing)
- Total new tests added: 144

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
- [x] Keyword search frontend UI (RFC-007 — `/keyword-search` page, 8 components, 26 tests, 12 commits)
- [ ] Save/Share functionality
- [ ] Multi-language support
- [ ] Batch query API
- [ ] History result snapshots (RFC-002 — store search response JSON for instant recall)

## Current Status

| Area | Status | Notes |
|------|--------|-------|
| Core Search | Complete | 84%+ accuracy |
| Answer Generation | Complete | Gemini 2.5 Flash |
| Multi-Agent | Complete | 5-paragraph output |
| CLI | Complete | Rich formatting |
| REST API | Complete | FastAPI + JWT |
| Keyword Search | Complete | RFC-006: 77,429 words, 1,651 roots |
| Landing Page | Complete | Utilitarian luxury redesign, non-technical |
| Frontend | Complete | Next.js 15 + Framer Motion |
| Docker Setup | Complete | PostgreSQL + Qdrant |
| Browser Tests | Passed | Login ✅, Search ✅, Compare ✅ (rich refs) |
| Multi-Translator | Complete | 8 Quran + 2 Turkish Bible |

## Known Issues

1. **Port conflicts**: Ensure no existing Qdrant on 6333
2. **Google OAuth**: Requires credentials in .env
3. **Rate limiting**: 50/day per user (configurable)
4. **SSE 30s gap**: During multi-agent generation, no heartbeats (partial mitigation via reconnection)
5. **Circuit breaker silent degradation**: Returns empty results instead of error (intentional for UX)
6. ~~**SSE streaming format mismatch**: Compare page essay not displayed~~ → **FIXED** (2026-01-28)
7. ~~**New Testament Citation Bug**: Backend agent generates citations with incorrect double brackets~~ → **FIXED** (2026-01-29, Issue #16 — citation system overhaul)
8. ~~**SSE Stats Format Mismatch**: Compare page stats (confidence, latency, verses) showing zero values~~ → **FIXED** (2026-01-29, Issue #17 — SSE message format alignment)
9. ~~**Arabic hamza normalization mismatch**: 137 roots unreachable via Arabic input~~ → **FIXED** (2026-02-01)
10. ~~**Null byte crash**: HTTP 500 on null byte input~~ → **FIXED** (2026-02-01)
11. ~~**Frontend module resolution regressions on `origin/main`**: missing aliases/files (`@/lib/logger`, `@/lib/api-client-setup`, `@/lib/utils/hebrew`, `@/lib/utils/verse-url`) block frontend checks~~ → **FIXED** (2026-02-09, modules restored + `.gitignore` exception for `frontend/lib/**`)

## Technical Debt (GitHub Issues)

| Issue | Description | Priority |
|-------|-------------|----------|
| [#10](https://github.com/aliozdenisik/Clarus/issues/10) | DRY: Verse detail extraction (~25 lines duplicated) | Medium |
| [#11](https://github.com/aliozdenisik/Clarus/issues/11) | DRY: Paragraph building (~35 lines duplicated) | Medium |
| [#12](https://github.com/aliozdenisik/Clarus/issues/12) | Playwright E2E test timing issues | Medium |
| [#13](https://github.com/aliozdenisik/Clarus/issues/13) | Parent Epic: Post-Deployment Cleanup | - |
| ~~[#75](https://github.com/aliozdenisik/Clarus/issues/75)~~ | ~~Better Auth Framework Fizibilite Analizi~~ | ~~High~~ → **CLOSED** |
| ~~[#57](https://github.com/aliozdenisik/Clarus/issues/57)~~ | ~~Redis Caching Infrastructure~~ | ~~High~~ → **CLOSED** |
| ~~[#17](https://github.com/aliozdenisik/Clarus/issues/17)~~ | ~~SSE stats message format mismatch~~ | ~~High~~ → **CLOSED** |
| ~~[#18](https://github.com/aliozdenisik/Clarus/issues/18)~~ | ~~Inconsistent search navigation options~~ | ~~Medium~~ → **CLOSED** |
| ~~[#19](https://github.com/aliozdenisik/Clarus/issues/19)~~ | ~~Missing Apocrypha book count~~ | ~~Low~~ → **CLOSED** |
| ~~[#20](https://github.com/aliozdenisik/Clarus/issues/20)~~ | ~~Compare page UI alignment~~ | ~~Medium~~ → **CLOSED** |
| ~~[#23](...)~~ | ~~RFC-006: Concordance & Keyword Search~~ | ~~High~~ → **CLOSED** |
| ~~[#25](...)~~ | ~~RFC-006: Kur'an Anahtar Kelime Arama~~ | ~~High~~ → **CLOSED** |
| ~~[#26](...)~~ | ~~Tanzil data source integration~~ | ~~Medium~~ → **CLOSED** |
| ~~NEW~~ | ~~Hebrew Latin b↔v ambiguity (`dabar` vs `davar`)~~ | ~~Low~~ → **FIXED** (2026-02-04) |
| ~~NEW~~ | ~~Hebrew Latin collision (`torah` → H2960 instead of H8451)~~ | ~~Low~~ → **FIXED** (2026-02-04) |
| ~~NEW~~ | ~~Greek Strong's number lookup bug (G2316 → None)~~ | ~~Medium~~ → **FIXED** (2026-02-04) |

## Evolution of Project

### Architecture Evolution

- **v1**: CLI-only Python application
- **v2**: Added multi-agent answer generation
- **v3**: Added FastAPI REST API
- **v3.1**: Removed Vue 3 frontend, CLI/API focus
- **v4**: Next.js 15 frontend with utilitarian luxury landing page (current)

### Key Decisions

| Decision | Rationale |
|----------|-----------|
| Remove frontend | Simplify maintenance, CLI sufficient for use case |
| Keep REST API | Enables integrations and programmatic access |
| CLI as primary | Power users prefer command-line, no auth friction |
