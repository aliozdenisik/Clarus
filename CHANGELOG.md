# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0-alpha] - 2026-02-10

### Added
- Backend CI/CD workflow (`.github/workflows/backend-ci.yml`) for automated testing on push/PR (#117)
  - Lint with Ruff (`ruff check .`)
  - Format check (`ruff format --check .`)
  - Type check with Pyright (`pyright`)
  - Run pytest tests (`uv run pytest tests/ -v`)
- Bible verse bounds validation in `verse_parser.py` using `BIBLE_VERSE_COUNTS` lookup table (#117)
- Structured logging with correlation IDs across frontend and backend
  - `frontend/lib/logger.ts` — Structured client-side logger (196 lines)
  - `frontend/lib/correlation.ts` — Correlation ID management (72 lines)
  - `frontend/lib/api-client-setup.ts` — API interceptors for request tracing (79 lines)
- Frontend utility modules for verse navigation
  - `frontend/lib/utils/verse-url.ts` — Verse reference parsing and URL building (277 lines)
- React-window virtualization for root browser (#91)
  - Renders only visible rows instead of all 1,600+ roots
  - `frontend/components/keyword-search/root-browser.tsx` updated

### Fixed
- Backend `.env` loading order (#119) — Loads before LLM stack initialization to ensure API keys are available
- Frontend lint warnings across 53 files (#120) — Resolved all ESLint warnings for clean CI
- Backend Pyright type checking debt across 20 files (#121) — Added explicit type annotations
- Backend Ruff linting debt across 63 files (#118) — Fixed E402/F401/F841 (import ordering, unused imports/variables)
- 5 previously excluded pytest tests now passing (#117)
  - Health endpoint tests updated for new `redis` field
  - Verse parser tests for Bible verse bounds validation
- Keyword search collection filtering (#108) — Respects user's selected collections in compare mode
- SSE streaming handler optimization (#92, #104) — Single-pass message processing instead of multiple filter/map passes
- React key stability migration (#94) — Replaced index-based keys with stable data identity keys across 53 files
- Zustand subscription optimization (#90) — Selector-based subscriptions prevent unnecessary re-renders

### Changed
- Frontend performance improvements (#91):
  - Batched DOM reads in tab indicator (useLayoutEffect)
  - Cached button bounds for magnetic hover effect
  - Virtualized root browser with react-window
- Bundle size optimizations (#85):
  - DevTools lazy-loaded in development only (100-200KB savings)
  - Direct date-fns imports for guaranteed tree-shaking (~40KB savings)
  - Recharts code-split with next/dynamic (~50KB savings)
- Backend testing infrastructure:
  - Uses `uv` package manager for reproducible installs
  - Pytest configuration excludes integration/benchmark scripts
  - All quality checks run on CI with continue-on-error
- Standardized project documentation
- Improved .gitignore configuration

## [0.2.0-alpha] - 2026-02-02

### Added
- Latin alphabet (Buckwalter) transliteration for Arabic roots and derived words (#29)
  - Backend: `root_buckwalter` and `word_transliterations` fields in API response
  - Frontend: Latin text displayed below Arabic in root card and derived word chips
- Interactive derived word selection updates charts and statistics in real-time (#28)
  - Clicking a derived word filters verses, recalculates surah distribution chart, and updates stats bar
  - Chart title reflects selected word filter

### Fixed
- In-verse word highlighting now works correctly (#30)
  - Backend returns `token_clean` (normalized) instead of raw `token` (with diacritics)
  - Removed redundant "Matched words" footer from verse cards
- Removed technical Buckwalter source badge from root card for cleaner UI (#31)

### Changed
- Keyword search navigation link added to main navigation bar

## [1.0.0] - 2024-01-27

### Added
- Initial release of Clarus
- Hybrid RAG search engine with Qdrant
- Multi-agent comparative analysis system
- FastAPI backend with JWT authentication
- Next.js frontend application
