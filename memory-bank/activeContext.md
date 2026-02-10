# Active Context

## Current Work Focus

**Date**: 2026-02-10

## Comprehensive Pre-Commit Hooks — COMPLETED ✅

**Date**: 2026-02-10
**Branch**: `feat/comprehensive-pre-commit-hooks`
**PR**: [#122](https://github.com/aliozdenisik/Clarus/pull/122)

Implemented industry-standard pre-commit hooks to prevent the recurring tech debt accumulation that required massive cleanup in issues #113-116 (282 ESLint warnings, 167 Pyright warnings, Ruff violations).

### Implementation Summary

**Pre-commit Config** (`.pre-commit-config.yaml` — 115 lines, 11 hooks):
- **File Quality**: trailing-whitespace, end-of-file-fixer, check-yaml, check-json, check-toml, check-merge-conflict, check-added-large-files (1MB), check-ast, debug-statements, check-case-conflict, mixed-line-ending, no-commit-to-branch (main/master)
- **Secret Detection**: gitleaks with custom `.gitleaks.toml` (OpenRouter + Google OAuth patterns)
- **Typo Detection**: codespell with Turkish/Arabic/Hebrew false-positive allowlist
- **Backend Linting**: ruff lint (20 rule sets) + ruff format (pre-commit stage)
- **Backend Types**: pyright (pre-push stage — slow)
- **Frontend Linting**: ESLint `--max-warnings=0` (pre-commit stage)
- **Frontend Formatting**: Prettier `--check` (pre-commit stage)
- **Frontend Types**: tsc `--noEmit` (pre-push stage — slow)

**Ruff Config** (`backend/pyproject.toml`):
- 20 rule sets: E, W, F, I, N, UP, S, B, A, C4, DTZ, T20, SIM, TCH, ASYNC, PERF, PIE, PGH, RUF
- 35 targeted ignores for project-specific patterns (Unicode text, FastAPI Depends, CLI print, async data loaders)
- Per-file-ignores for tests/, scripts/, __init__.py, main.py
- Started with 1,363 violations → all resolved

**Frontend Tooling**:
- `.prettierrc.json` created (semi:false, singleQuote:false, tabWidth:2, tailwindcss plugin)
- `.prettierignore` created (excludes generated API client, .next, out)
- `eslint.config.mjs` updated with eslint-config-prettier as last config
- `package.json` updated with format/format:check scripts + 3 new devDependencies

**CI Hardening**:
- `.github/workflows/backend-ci.yml` — removed `continue-on-error: true` from lint/format/typecheck (now blocking)

**Code Fixes**:
- Fixed UP038 isinstance modernization (tuple → union syntax) in 3 files
- Fixed mixed line endings in Turkish Quran XML and morphology data files
- Codespell allowlist for Turkish/Hebrew/Greek domain terms (sme, shema, sizin, vai, etc.)

**Files Deleted** (cleanup):
- `.secrets.baseline` (replaced by gitleaks)
- `.pre-commit-config.yaml.backup`
- `test_precommit.py`, `scripts/setup-pre-commit.sh` (research artifacts)
- `PRE_COMMIT_PLAN.md`, `PRE_COMMIT_SETUP.md`, `SECURITY-PRECOMMIT-RESEARCH.md`

**Verification**: All 17 pre-commit hooks pass on full repo (`pre-commit run --all-files` ✅)

---

## Issue #91: Frontend Performance Hotspots — COMPLETED ✅

**Date**: 2026-02-09

Resolved three frontend performance bottlenecks identified in issue #91:

- Consolidated layout reads/writes in `vercel-tabs` into a single `useLayoutEffect` to reduce layout thrashing.
- Added root list virtualization in `root-browser` using `react-window` `List` for 1,651+ roots.
- Cached magnetic button bounds on `mouseenter` and reused them during `mousemove` to avoid repeated `getBoundingClientRect()` calls.

**Verification:**
- `npx tsc --noEmit` ✅
- `npm test -- --run __tests__/keyword-search-page.test.tsx __tests__/search-tabs.test.tsx` ✅
- `npm test -- --run` ✅ (19 files, 228 tests passed)
- `npm run build` ✅

**Key files updated:**
- `frontend/components/ui/vercel-tabs.tsx`
- `frontend/components/keyword-search/root-browser.tsx`
- `frontend/components/ui/magnetic-button.tsx`
- `frontend/package.json`

## Issue #94: React Stable Keys Migration — COMPLETED ✅

**Date**: 2026-02-09

Resolved frontend performance/reconciliation issue by replacing index-based React keys (`key={i}` / `key={index}`) across search, compare, history, browse pages, and shared UI components.

**What changed:**
- Replaced high-risk dynamic list keys with data-derived stable keys (search results, parsed citations, paragraph blocks, repeated citation tags).
- Standardized placeholder keys for skeleton loaders with deterministic prefixes to avoid key collisions during loading transitions.
- Updated shared components (`verse-card`, `text-rotate`, `slider`, `navbar`, `typewriter`, `root-browser`) to remove direct index keys while preserving animation behavior.

**Verification:**
- `npx tsc --noEmit` ✅
- `npm test -- --run` ✅ (19 files, 228 tests passed)
- `npm run build` ✅ (Next.js production build successful)

**Key files updated:**
- `frontend/app/search/page.tsx`
- `frontend/app/compare/page.tsx`
- `frontend/app/history/page.tsx`
- `frontend/app/keyword-search/page.tsx`
- `frontend/components/keyword-search/verse-card.tsx`
- `frontend/components/ui/text-rotate.tsx`
- `frontend/components/ui/slider.tsx`

---

## RFC-009: Verified Source Data — COMPLETED ✅

**Date**: 2026-02-09

Completed RFC-009 Tier 1: Multi-translator Quran support (8 Turkish translations from Tanzil XML) and Turkish Bible indexing (OSIS XML). All collections indexed and verified.

**Implementation Summary (13 code tasks + indexing + verification):**

**Data Loaders:**
- TanzilLoader: Parses Tanzil XML for 8 Turkish Quran translations (6,236 verses each)
- OsisLoader: Parses OSIS XML for Turkish Bible (OT: 22,724 + NT: 7,458 verses)

**Indexing:**
- 8 Quran collections: quran_tr_{ates,bulac,diyanet,ozturk,vakfi,yazir,yildirim,yuksel}
- 2 Turkish Bible collections: bible_tr_ot, bible_tr_nt
- Old quran_tr collection deleted
- Total: 13 collections, ~123,000 vectors

**Code Changes (12 commits):**
- Data loaders: tanzil_loader.py, osis_loader.py
- Indexer: QuranIndexer multi-translator, TurkishBibleIndexer
- Search: QuranSearcher translator routing
- RAG: UltimateRAG, ComparativeRAG translator params
- API: All endpoints accept translator parameter
- CLI: --translator flag, asyncio.run() fixes
- Frontend: Translator selector UI
- Tests: Updated collection references

**Verification Results:**
- `python main.py info`: 13 collections, all green ✅
- `python main.py search "sabır ve namaz"`: Diyanet results ✅
- `python main.py search --translator yazir`: Yazır-specific results ✅
- `python main.py compare "Yaratılış"`: 93% confidence, 80 verses ✅
- All 8 Quran collections: 6,236 verses each ✅
- bible_tr_ot: 22,724, bible_tr_nt: 7,458 ✅

**Known Gap:** CLI `search-bible --language tr` not implemented (Turkish Bible collections indexed but no CLI route yet)

**Key Files:**
- `backend/src/tanzil_loader.py` — Tanzil XML parser
- `backend/src/osis_loader.py` — OSIS XML parser
- `backend/src/indexer.py` — QuranIndexer + TurkishBibleIndexer
- `backend/data/tanzil/` — 8 Turkish Quran XML files
- `backend/data/turkish_bible.xml` — Turkish Bible OSIS XML

---

## Better Auth Framework Integration (Issue #75) - COMPLETED ✅

**Date**: 2026-02-06

Completed full integration of Better Auth framework (not just feasibility study). Replaced custom JWT authentication with industry-standard auth framework.

**Implementation Summary (12 tasks, 4 waves):**

**Wave 1: Better Auth Server & Schema**
1. Better Auth server configured with JWT plugin and Next.js handler
2. Database schema migration (users → users_legacy, new user_stats table)
3. Feasibility report created at `docs/better-auth-feasibility.md` (GO recommendation)

**Wave 2: Frontend Auth UI & Backend Integration**
4. Better Auth React client + sign-in/sign-up pages with Better Auth UI
5. JWKS-based JWT validator for FastAPI backend
6. API key authentication for CLI access

**Wave 3: Migration Scripts & State Management**
7. User migration script from legacy auth to Better Auth
8. Rate limiting migrated to Better Auth user IDs
9. Frontend auth state migrated to Better Auth hooks

**Wave 4: Endpoint Wiring & Cleanup**
10. All protected endpoints wired to Better Auth JWT validation
11. Legacy JWT, token blacklist, and old login page removed (7 files, 1,661 lines)
12. Documentation updated (this file)

**Architecture:**
- **Frontend**: Better Auth on Next.js (port 3000) with JWT plugin
- **Backend**: JWKS validator validates JWT tokens from Better Auth
- **Bridge**: Backend fetches public keys from `http://localhost:3000/api/auth/jwks`
- **CLI Access**: API key authentication for non-browser workflows

**Key Files:**
- `frontend/lib/auth.ts` — Better Auth server config
- `frontend/app/api/auth/[...all]/route.ts` — Auth API handler
- `frontend/app/(auth)/sign-in/page.tsx` — Sign-in page
- `frontend/app/(auth)/sign-up/page.tsx` — Sign-up page
- `backend/app/auth/jwks_validator.py` — JWT validator
- `backend/app/api/auth.py` — API key auth + /me endpoint
- `backend/scripts/migrate_users.py` — User migration script

**Database Changes:**
- Tables added: `user`, `session`, `account`, `verification`, `jwks` (Better Auth)
- Tables modified: `users` → `users_legacy` (kept for 30 days)
- Tables created: `user_stats` (Clarus-specific: query count, API key)

**Legacy Code Removed:**
- `backend/app/auth/token_blacklist.py`
- `backend/app/auth/schemas.py`
- `frontend/lib/auth/auth-context.tsx`
- `frontend/app/login/page.tsx`
- `frontend/app/register/page.tsx`
- Frontend auth tests (auth-context.test.tsx, login.test.tsx)
- Net reduction: -1,661 lines

**11 Commits:**
- `b7113c6` feat(auth): configure Better Auth server with JWT plugin
- `06ff046` feat(db): create user_stats table, rename legacy users
- `6b02046` docs: add Better Auth feasibility report
- `3cfb0e4` feat(frontend): add Better Auth client and sign-in/sign-up pages
- `b7421a9` feat(backend): add JWKS-based JWT validator
- `68eff87` feat(backend): add API key authentication for CLI
- `199e063` feat(migration): add user migration script
- `94064fe` feat(backend): migrate rate limiting to Better Auth user IDs
- `482f4e6` refactor(frontend): migrate auth state to Better Auth hooks
- `296eab3` feat(auth): wire Better Auth JWT validation into all endpoints
- `7c4c609` refactor(auth): remove legacy JWT and token blacklist

**Feasibility Report:** `docs/better-auth-feasibility.md` (GO recommendation)

---

## Redis Caching Infrastructure (Issue #57) - COMPLETED ✅

- Replaced DiskCache with Redis Stack 7.2
- 5 caching layers: LLM semantic cache, embedding cache, search result cache, rate limiting, JWT blacklist
- Fail-open resilience across all Redis operations
- Health endpoint reports Redis status (connected/disconnected/degraded)
- DiskCache removed from requirements.txt and codebase

**Date**: 2026-02-04

### Bible Keyword Search Fixes (2026-02-04) - COMPLETE ✅

Fixed 3 issues in Bible keyword search after industry-standard research on Hebrew/Greek transliteration.

**Issue 1: Hebrew b↔v Ambiguity**
- **Problem**: "dabar" returns nothing, but "davar" works (DB has `da.var` → `davar`)
- **Root Cause**: Hebrew ב is transliterated as 'b' (with dagesh) or 'v' (without dagesh)
- **Academic Research**: ISO 259, SBL, ALA-LC all preserve this distinction
- **Solution**: Dual-indexing in `_load_strongs_cache()` — both variants point to same Strong's
- **Reference**: ALA-LC Romanization Tables, Sefaria implementation

**Issue 2: Torah Collision**
- **Problem**: "torah" → H2960 (burden, 2 occ) instead of H8451 (law, 219 occ)
- **Root Cause**: Both `to.rach` and `to.rah` normalize to "torah" due to `ch→h` rule
- **Solution**: Sort `_transliteration_map` lists by occurrence count (descending)
- **Reference**: Standard IR practice for disambiguation

**Issue 3: Greek Strong's Number Bug**
- **Problem**: G2316 search returns 1307 occurrences but `strong_number` = None
- **Root Cause**: Greek searches translate Strong's → lemma, but lose the Strong's number
- **Solution**: Preserve Strong's number in `_search_by_lemma()` when user explicitly searched G####

**Files Modified:**
- `backend/src/bible_morphology.py` — Dual-indexing, occurrence sorting, Strong's preservation
- `backend/src/hebrew_normalizer.py` — No changes (academic research rejected simple v→b normalization)

**Test Results (13/13 PASS):**
| Test | Expected | Result |
|------|----------|--------|
| dabar | H1697 | ✓ H1697 (1440 occ) |
| davar | H1697 | ✓ H1697 (1440 occ) |
| torah | H8451 | ✓ H8451 (219 occ) |
| elohim | H0430 | ✓ H0430 (2596 occ) |
| shalom | H7965 | ✓ H7965 (223 occ) |
| chesed | H2617 | ✓ H2617 (247 occ) |
| logos | λόγος | ✓ λόγος (330 occ) |
| theos | θεός | ✓ θεός (1307 occ) |
| agape | ἀγάπη | ✓ ἀγάπη (116 occ) |
| G2316 | G2316 + θεός | ✓ G2316, θεός, "theós" |
| G2222 | G2222 + ζωή | ✓ G2222, ζωή |
| H1697 | H1697 | ✓ H1697 (1440 occ) |
| H8451 | H8451 | ✓ H8451 (219 occ) |

### Bible Keyword Search Verification (2026-02-04) - COMPLETE ✅

Verified occurrence counts against Blue Letter Bible (authoritative concordance).

**Verification Results:**
| Strong's | Word | Our Count | BLB Count | Delta | Status |
|----------|------|-----------|-----------|-------|--------|
| H1697 | dabar | 1,440 | 1,439 | +1 (+0.07%) | ✓ PASS |
| H8451 | torah | 219 | 219 | 0 (0.00%) | ✓ EXACT |
| H430 | elohim | 2,596 | 2,606 | -10 (-0.38%) | ✓ PASS |
| G2316 | theos | 1,307 | 1,318 | -11 (-0.83%) | ✓ PASS |

**Root Cause of Discrepancies (all <1% — acceptable):**
1. **Text traditions differ**: We use OSHB (Open Scriptures Hebrew Bible) + MorphGNT, BLB uses WLC (Westminster Leningrad Codex) + Textus Receptus
2. **Greek manuscript base**: MorphGNT is based on NA27/NA28 (critical text), BLB uses Textus Receptus (Majority Text)
3. **Counting methods**: Some count word forms, others count lemma occurrences

**Conclusion**: All discrepancies are under 1%, which is expected variance between different manuscript traditions. Our data sources (OSHB + MorphGNT) are academically rigorous and the counts are accurate for their respective text bases.

**No code changes required** — verification confirms correctness.

### Accuracy Disclaimer UI (2026-02-04) - COMPLETE ✅

Added user-facing accuracy verification UI to Bible Word Search page.

**Component Created:** `frontend/components/keyword-search/accuracy-disclaimer.tsx`

**Features:**
- Expandable panel (collapsed by default)
- "Clarus can make mistakes. Verify important information." disclaimer
- Verification table comparing Clarus counts vs Blue Letter Bible
- Color-coded status badges (EXACT = green, PASS = amber)
- Delta percentages shown for each entry
- Links to Blue Letter Bible external reference
- Data source information (OSHB, MorphGNT vs WLC, Textus Receptus)

**Verification Data Shown:**
| Strong's | Word | Clarus | BLB | Δ | Status |
|----------|------|--------|-----|---|--------|
| H1697 | dabar | 1,440 | 1,439 | +0.07% | PASS |
| H8451 | torah | 219 | 219 | 0.00% | EXACT |
| H430 | elohim | 2,596 | 2,606 | -0.38% | PASS |
| G2316 | theos | 1,307 | 1,318 | -0.83% | PASS |

**Integration:**
- Shows only for Bible modes (Hebrew OT / Greek NT)
- Appears at bottom of search results
- Separated by subtle border

**Tests Added (8):**
- Renders collapsed disclaimer message
- Expands to show verification table on click
- Displays verification data with correct Strong's numbers
- Displays verification data with word names
- Shows Blue Letter Bible link
- Shows status badges for verification results
- Displays data source information
- Collapses when clicked again

**Files Created:**
- `frontend/components/keyword-search/accuracy-disclaimer.tsx` (162 lines)

**Files Modified:**
- `frontend/app/keyword-search/page.tsx` — Import + integration
- `frontend/__tests__/keyword-search-components.test.tsx` — 8 new tests

---

### Hebrew Latin Transliteration Fix (2026-02-03) - COMPLETE ✅

Fixed 11 Hebrew Latin test failures in Word Search feature. Users can now search with ASCII queries like `elohim`, `chesed`, `ahab` and get correct Strong's Concordance matches.

**Problem:**
- Strong's transliterations use scholarly notation: `ʼĕlôhîym`, `chêçêd`, `shâmaʻ`
- Users type simple ASCII: `elohim`, `chesed`, `shama`
- No match → search fails → 0 results

**Solution: Biblical Hebrew Normalization**
- Implemented `normalize_transliteration_for_lookup()` in `hebrew_normalizer.py`
- Transforms scholarly notation to ASCII using industry-standard rules:
  - Unicode NFD + strip combining chars (like `unidecode`)
  - Biblical Hebrew rules: `ch→h` (Het), `ç→s` (Samekh), `ym→m` (plural), `ow→o` (holem-vav)
- Cache builds normalized keys at startup: `_transliteration_map["elohim"] = ["H0430"]`
- Zero-padded Strong's numbers for `bm_words` compatibility

**Test Results:**
| Metric | Before | After |
|--------|--------|-------|
| Overall Pass Rate | 91.3% (137/150) | **98.7% (148/150)** |
| Hebrew Latin Tests | 11 FAIL | **0 FAIL** |

**Files Modified:**
- `backend/src/hebrew_normalizer.py` — Fixed `ç→s` ordering (before NFD)
- `backend/src/bible_morphology.py` — Added normalized ASCII keys + zero-padded format

**Documentation:** `backend/docs/HEBREW_TRANSLITERATION.md`

**Industry Standard Compliance:**
- Matches Sefaria's approach (Unicode normalization + Biblical Hebrew rules)
- Exceeds plain `unidecode` (handles `ym→m`, `ch→h`, `ow→o`)

---

### Security Audit (2026-02-03) - COMPLETE ✅

Comprehensive security audit conducted identifying 30 vulnerabilities across 4 severity levels.

**Summary:**
| Severity | Count | Status |
|----------|-------|--------|
| CRITICAL | 7 | ⚠️ Immediate action required |
| HIGH | 10 | 🔶 Fix within 1 week |
| MEDIUM | 9 | 🔷 Fix within sprint |
| LOW | 4 | ℹ️ Monitor and fix |

**Critical Findings:**
1. Exposed API keys in `.env` (OpenRouter, Google OAuth, JWT secret)
2. Hardcoded default JWT secret in `config.py`
3. JWT token exposed in query parameters (SSE endpoint)
4. SQL injection anti-pattern in morphology search
5. Unauthenticated API endpoints (keyword_search, metadata)
6. Debug mode hardcoded to True
7. CORS wildcard methods/headers

**Documentation:**
- Local: `/docs/security/SECURITY_AUDIT_2026-02-03.md`
- GitHub Issues: #39-#49 (11 issues created)

**Priority Actions:**
1. **TODAY**: Rotate all exposed credentials, remove `.env` from git history
2. **THIS WEEK**: Add auth to all endpoints, fix JWT in query params, add security headers
3. **THIS SPRINT**: Migrate to HttpOnly cookies, add CSRF protection, password validation

**GitHub Issues Created:**
- #39: [SECURITY] CRITICAL: Exposed API Keys and Secrets
- #40: [SECURITY] CRITICAL: Hardcoded Default JWT Secret
- #41: [SECURITY] CRITICAL: JWT Token Exposed in Query Parameters
- #42: [SECURITY] CRITICAL: SQL Injection via String Interpolation
- #43: [SECURITY] CRITICAL: Unauthenticated API Endpoints
- #44: [SECURITY] CRITICAL: Debug Mode and CORS Misconfiguration
- #45: [SECURITY] HIGH: Authentication and Session Management
- #46: [SECURITY] HIGH: Input Validation and Output Encoding
- #47: [SECURITY] HIGH: Missing Security Headers
- #48: [SECURITY] MEDIUM: Password Policy and Account Security
- #49: [SECURITY] LOW: Minor Security Improvements

---

### Keyword Search QA: SPECIAL_TERMS Fix (2026-02-02) - COMPLETE ✅

Fixed the last 2 known limitations in keyword search: `الله` (Allah) and `quran` now resolve to correct roots.

**Problem 1:** `الله` → root لهه (0 occurrences). DB has token `ٱلله` (hamzatu'l-wasl ٱ U+0671), user types `الله` (regular alef). Tashaphyne gives wrong root.
**Problem 2:** `quran` → root قرن (horn, 36 occ) instead of قرأ (read, 88 occ). Vowel stripping produces "qrn".

**Solution:** `SPECIAL_TERMS` dictionary in `quran_morphology.py` maps well-known terms directly to correct roots, bypassing algorithmic extraction. Also added hamzatu'l-wasl normalization (ٱ→ا) in `arabic_normalizer.py`.

**Files Modified:**
- `backend/src/quran_morphology.py` — SPECIAL_TERMS dict (18 entries), `_find_root()` early lookup
- `backend/src/arabic_normalizer.py` — ٱ→ا normalization in `normalize_arabic()`

**Test Results:** 20/20 PASS (API + Playwright web verification). See `test-results-keyword-search.md`.

### RFC-007: Quran Keyword Search Frontend (2026-02-02) - COMPLETE ✅

Built a dedicated `/keyword-search` page consuming the morphological keyword search API (3 endpoints), presenting root-based Arabic word search results in a scholarly concordance UI matching Clarus's utilitarian luxury design language.

**Architecture:**
- Next.js 15 page at `/keyword-search` with 8 custom components
- Recharts horizontal bar chart for surah distribution (dark theme, academic styling)
- Verse cards with Arabic (Uthmani) + Turkish translation + word highlighting
- Root browser tab with search/filter for all 1,651 roots
- Navigation integration (desktop dropdown + mobile menu)
- OpenAPI client regeneration with keyword search types

**Components Created (8):**
- `frontend/app/keyword-search/page.tsx` — Main page (~437 lines)
- `frontend/components/keyword-search/search-input.tsx` — Arabic/Latin search input
- `frontend/components/keyword-search/root-card.tsx` — Arabic root display with source badge
- `frontend/components/keyword-search/stats-bar.tsx` — Three-column statistics
- `frontend/components/keyword-search/derived-words.tsx` — Clickable word filter tags
- `frontend/components/keyword-search/surah-chart.tsx` — Recharts horizontal bar chart
- `frontend/components/keyword-search/verse-card.tsx` — Verse display with highlighting
- `frontend/components/keyword-search/pagination.tsx` — Page navigation
- `frontend/components/keyword-search/root-browser.tsx` — Browse all 1,651 roots

**Tests:** 26 keyword-search specific tests (10 integration + 16 unit), 244/244 total passing

**Git Commits (12):**
- `d637a49` chore(frontend): regenerate OpenAPI client with keyword search types
- `14eab0c` feat(frontend): add keyword search page scaffold with search input
- `44c903a` feat(frontend): add root card, stats bar, and derived words components
- `ca61e81` feat(frontend): add Recharts surah distribution chart with academic styling
- `6d91712` feat(frontend): add verse card with Arabic text, Turkish translation, and word highlighting
- `c09bc50` feat(frontend): add pagination component for keyword search
- `7d8b952` feat(frontend): add root browser tab with search and filtering
- `92f590a` feat(frontend): add Word Search to navigation menu
- `0b5aa48` feat(frontend): add empty state, loading skeletons, and error handling for keyword search
- `faedcdd` test(frontend): add keyword search page and component tests
- `5d9b6f6` fix(frontend): display surah names in Latin transliteration and link to specific verses
- `1fc1ef0` fix(frontend): correct API response data nesting for surah transliterations and translations

**Bugs Fixed During QA:**
1. Surah names displayed in Arabic instead of Latin transliteration — fetched metadata, built transliteration map
2. API response nesting: `response.data.data.X` (two levels of `.data`) due to MetadataResponse wrapper + SDK layer

### RFC-006: Quran Morphological Root-Based Keyword Search (2026-02-01) - COMPLETE ✅

Implemented morphological root-based keyword search for the Quran, enabling academics to find all words derived from an Arabic root with frequency analysis, verse locations, and surah distribution.

**Architecture:**
- PostgreSQL deterministic lookup (3 tables: surahs, ayahs, words) + Tashaphyne algorithmic fallback
- Hybrid root extraction: DB exact match → prefix stripping → Tashaphyne
- Buckwalter Latin input support with fuzzy matching via pg_trgm
- CLI subcommand: `python main.py keyword-search "كتب"` (Arabic) or `keyword-search "ktb"` (Latin)
- REST API: `POST /api/search/keyword/` + `GET /api/search/keyword/roots` + `GET /api/search/keyword/root/{root}`

**Data:**
- 114 surahs, 6,236 ayahs, 77,429 words, 1,651 unique roots
- Dual-layer Arabic text: Uthmani (display) + Simple Clean (search)
- Buckwalter transliteration for Latin input support

**Files Created (7):**
- `backend/requirements.txt` — Added tashaphyne, pyarabic
- `backend/app/models.py` — QMSurah, QMAyah, QMWord models
- `backend/scripts/create_morphology_tables.py` — Schema creation
- `backend/scripts/setup_quran_morphology.py` — ETL pipeline
- `backend/src/arabic_normalizer.py` — Normalization utilities
- `backend/src/quran_morphology.py` — Search service
- `backend/app/api/keyword_search.py` — REST API router
- `backend/app/schemas/keyword_search.py` — Pydantic models

**Files Modified (2):**
- `backend/main.py` — CLI subcommand + dispatch
- `backend/app/main.py` — Router registration

**Verification Results (20 tests):**
- ✅ CLI Arabic: كتب (319), صلو (99), أمن (879), قول (1722), علم (854)
- ✅ CLI Latin: ktb (319), Slw (3), Amn (879), qwl (1722), Elm (854)
- ✅ API Arabic: All 5 roots match CLI counts
- ✅ API Latin: All 5 roots match CLI counts
- ✅ Regression: `python main.py info` works, `/api/health` healthy
- ✅ Consistency: CLI and API return identical `total_occurrences` for same root

**Git Commits (8):**
- `ac47631` feat(morphology): add tashaphyne and pyarabic dependencies
- `b4aa332` feat(morphology): add PostgreSQL schema for Quran morphological search
- `862d557` feat(morphology): add ETL pipeline for Quran morphological data
- `6f5ac75` feat(morphology): add search service with Arabic normalization
- `b532aba` feat(morphology): add keyword-search CLI subcommand
- `b532aba` feat(morphology): add REST API endpoints for keyword search
- `bad5652` fix(morphology): fix pg_trgm fuzzy match operator in Buckwalter search
- `a09f16c` fix(morphology): fix Arabic hamza normalization mismatch and null byte crash

**Bug Fixed During Verification:**
- Fixed pg_trgm fuzzy match operator: `%%` → `%` in SQLAlchemy text() queries (Amn, Elm now work)

**Hamza Normalization Fix (2026-02-01):**
- Fixed Arabic hamza mismatch: `normalize_arabic()` strips hamza (أ→ا) but DB `root` column preserves hamza
- Added SQL-side REPLACE normalization in `_find_root_arabic()` Step 3
- 137 hamza roots (8% of 1,651) now findable: أله (2851), أمن (879), أيي (597), etc.
- Null byte input crash fixed: strip `\x00` before DB query

**Security Testing (48 vectors, 7 categories):**
- SQL Injection: 10/10 ✅ (parameterized queries via SQLAlchemy)
- XSS/Template Injection: 5/5 ✅
- Command Injection: 6/6 ✅
- DoS/Boundary: 7/7 ✅
- Malformed JSON: 9/9 ✅
- Unicode Attacks: 7/7 ✅
- Zero vulnerabilities found

**GitHub Issues Closed:**
- #23 RFC-006: Concordance & Keyword Search (English proposal) ✅
- #25 RFC-006: Kur'an Anahtar Kelime Arama (Turkish proposal) ✅
- #26 Replace Quran data with Tanzil source ✅

**All 8 commits pushed to `origin/main`.**

### GitHub Project Board — Batch Issue Resolution (2026-01-29) - NEW

Processed 4 Todo issues from the GitHub Projects (V2) board (#2 "Clarus Ussues and Pull Requests"). All issues solved, committed, and closed.

**Issue #17 — [Bug] Stats Zeroed Out** (P0)
- **File:** `frontend/app/compare/page.tsx` (lines 299-320)
- **Root Cause:** SSE message format mismatch — frontend looked for `m.stats` but backend sends `{"type": "stats", "data": {...}}`
- **Fix:** `m.stats` → `m.type === "stats"`, `statsMsg.stats.*` → `statsMsg.data.*`, added `total_citations` extraction
- **Commit:** `a7f560f`

**Issue #18 — [UX] Inconsistent Search Navigation**
- **File:** `frontend/components/layout/navigation.tsx`
- **Root Cause:** Header "Search" dropdown had only 2 options (Quran/Bible) but search page supports 4 collections
- **Fix:** Replaced with 4-option dropdown: Quran Search, Old Testament Search, New Testament Search, Apocrypha Search
- **Updated both:** Desktop dropdown + Mobile menu
- **Commit:** `22bfe89`

**Issue #19 — [UI] Missing Apocrypha Book Count**
- **File:** `frontend/components/layout/navigation.tsx`
- **Root Cause:** Browse menu showed "Apocrypha" without book count (others had counts)
- **Fix:** Changed to "Apocrypha (14 Books)" — verified from `bible_kjva.json` (books with nr ≥ 67)
- **Commit:** `0bd9c60`

**Issue #20 — [UI/UX] Compare Page UI Alignment**
- **File:** `frontend/app/compare/page.tsx`
- **Root Cause:** Compare page used different visual language than the redesigned Search page
- **Fix:** Aligned 7 design elements with Search page standards:
  1. Added ambient teal radial gradient background
  2. Title: `text-3xl font-bold` → `font-display text-4xl font-normal tracking-tight`
  3. Subtitle: Added `text-sm` sizing
  4. Search input: `<Input>` component → custom `rounded-xl` input with search icon
  5. Button: Positioned inside input, accent bg + dark text
  6. Paragraph sections: Added "AI INTERPRETATION" label + `border-l-2` accent left border
  7. Added ornamental diamond dividers between sections
- **Commit:** `4309d4c`

**Git Commits (4):**
- `a7f560f` fix(frontend): align SSE stats parsing with backend message format (#17)
- `22bfe89` fix(frontend): align search navigation with 4-collection search modes (#18)
- `0bd9c60` fix(frontend): add book count for Apocrypha in navigation menu (#19)
- `4309d4c` feat(frontend): align compare page UI with search page design standards (#20)

### Citation System Overhaul — Issue #16 (2026-01-29) - NEW

Replaced the fragile bracket-based citation system with a defense-in-depth architecture resolving GitHub Issue #16 (NT agent double-bracket citations).

**Architecture: Sanitizer → Parser → HoverCard**

1. **Backend Citation Sanitizer** (`backend/src/citation_sanitizer.py`)
   - Pure-function post-processing: strips double brackets, trims whitespace, normalizes commas
   - Wired into `backend/app/api/compare.py` — sanitizes ALL agent output before API response
   - Idempotent transformations (safe to apply multiple times)

2. **Strengthened LLM Prompts** (`multi_agent_answer_generator.py`, `comparative_answer_generator.py`)
   - All 4 specialist agents + comparative generator have explicit anti-double-bracket rules
   - "ATIF FORMAT KURALLARI" section added to each prompt
   - Zero `[[` patterns in prompt files (verified via grep)

3. **Rewritten Frontend Parser** (`frontend/lib/utils/parse-citations.ts`)
   - Tighter regex: only matches `[content]` containing colon `:` (filters `[sic]`, `[Note]`)
   - No bracket characters in output — citations are clean objects
   - Range expansion: `Bakara:4-5` → individual verse citations
   - Comma handling: `Enfal:2, 9` → expanded references
   - 35 comprehensive Vitest tests (all passing)

4. **Radix HoverCard Component** (`frontend/components/compare/citation-hover-card.tsx`)
   - Accent-colored inline text links (no brackets visible)
   - Hover shows: source badge, reference title, verse text preview, "Open verse" link
   - Framer Motion animations (springPresets.snappy)
   - Graceful fallback when verse_details missing

5. **Integration** (`backend/app/api/compare.py`, `frontend/app/compare/page.tsx`)
   - Backend: sanitize_citations() applied to all 5 commentaries + citations dict
   - Frontend: InlineCitation passes verseDetail + onNavigate to HoverCard

**Files Created:**
- `backend/src/citation_sanitizer.py` (127 lines)
- `frontend/components/compare/citation-hover-card.tsx` (97 lines)

**Files Modified:**
- `backend/src/multi_agent_answer_generator.py` — prompt strengthening
- `backend/src/comparative_answer_generator.py` — prompt strengthening
- `backend/app/api/compare.py` — sanitizer integration
- `frontend/lib/utils/parse-citations.ts` — rewritten parser
- `frontend/components/compare/inline-citation.tsx` — HoverCard wrapper
- `frontend/app/compare/page.tsx` — passes verseDetail to InlineCitation
- `frontend/__tests__/parse-citations.test.tsx` — 35 comprehensive tests
- `frontend/__tests__/inline-citation.test.tsx` — updated tests

**Git Commits (6):**
- `dc308df` feat(backend): add citation sanitizer for LLM output normalization
- `5bbe176` fix(prompts): strengthen citation format rules to prevent double-bracket drift
- `6c3606b` test(frontend): add comprehensive citation parser unit tests
- `b343c1a` refactor(frontend): rewrite citation parser with tighter pattern matching
- `c197ba2` feat(frontend): add HoverCard citation component with verse preview
- `6fe44f6` feat: integrate citation sanitizer across compare pipeline

### Confidence Scoring Overhaul (2026-01-30) - NEW

Replaced the flawed 6-signal weighted arithmetic mean (which had a structural ceiling of ~72%) with a **Two-Phase Sigmoid-Calibrated** system aligned with industry standards (Perplexity/Cohere).

**Problem:**
- `llm_confidence` signal was always 0.0 (dead weight)
- `citation_coverage` penalized concise answers (expected 100% of context to be cited)
- Arithmetic mean diluted strong signals with weak ones
- Result: Excellent answers scored ~70%, mediocre ones ~60% (no differentiation)

**Solution (2.0 Methodology):**
1. **Phase 1: Retrieval Confidence** (Search Quality)
   - Median RRF Score (Sigmoid calibrated)
   - Score Separation (Top vs 5th result ratio)
   - Result Coverage

2. **Phase 2: Answer Quality** (Groundedness)
   - Citation Density (Citations per paragraph) instead of coverage ratio
   - Top-K Usage (Did LLM use the best results?)
   - Answer Substance (Word count)

3. **Hybrid Fusion:**
   - Geometric-Arithmetic blend: Bad retrieval tanks the score (GIGO principle)
   - Final Sigmoid Calibration: Maps raw scores to meaningful **40-95%** range

**Files Modified:**
- `backend/src/confidence_scorer.py` - Complete rewrite
- `backend/src/answer_generator.py` - Integration
- `backend/src/multi_agent_answer_generator.py` - Integration & cleanup
- `backend/src/comparative_answer_generator.py` - Integration
- `backend/main.py` - Updated CLI display
- `docs/CONFIDENCE_SCORING.md` - New documentation

**Git Commits (8):**
- `25b3540` feat(cli): display confidence breakdown in search/ask/compare output
- `113f67e` feat(api): add confidence_breakdown to API and SSE responses
- `25cf88e` feat(multi-agent): replace LLM confidence averaging with objective ConfidenceScorer
- `0d464d0` feat(answer): integrate objective confidence scoring into single-source answer generator
- `5fd7506` feat(rag): expose RRF score statistics from search pipeline
- `0c8a6f1` feat(search): preserve original Qdrant similarity scores before RRF overwrite
- `b67e8ad` feat(confidence): add ConfidenceScorer module with 5-signal computation
- `(latest)` refactor(confidence): implement two-phase sigmoid calibration

### RFC-003: Multilingual Query Translation (2026-01-30) - NEW

Implemented Phase 1 of RFC-003: Automatic multilingual query translation so users can search in any of 8 supported languages and get results back in their language.

**Architecture: Detect → Translate → Search → Translate Response**

1. **QueryTranslator Module** (`backend/src/query_translator.py`, 614 lines)
   - Single LLM call via OpenRouter (`google/gemini-2.5-flash-lite`) for language detection + translation
   - Heuristic pre-filters: Turkish chars + quran → skip LLM; pure ASCII + bible → skip LLM
   - Zero new dependencies (VPS constraint — no FastText, no lingua-py)
   - Supported languages: en, tr, es, fr, it, pt, ar, de

2. **Backend Integration**
   - `UltimateRAG`: Translation in `search_quran()`, `search_bible()`, `ask_quran()`, `ask_bible()`
   - `ComparativeRAG`: Parallel translation in `_translate_query_parallel()`
   - API endpoints: `language` request field + `detected_language` response field
   - Response translation for compare + SSE streaming endpoints
   - Cross-lingual cache metadata with `source_language` tracking

3. **Frontend Integration**
   - `LanguageSelector` component (Radix DropdownMenu) in search + compare pages
   - Session-based language selection (no persistence)
   - Badge shows: "🌐 Auto", "🌐 Auto (ES)", or "🌐 ES"

4. **Testing**
   - 15 unit tests for QueryTranslator (mocked LLM)
   - 40 translation accuracy tests across 8 language categories
   - 12 multilingual retrieval accuracy test cases (EN→Quran, TR→Bible, ES→Quran, FR→Bible)
   - Retrieval accuracy test now includes Stage 0: Query Translation + native vs translated metrics

**Files Created:**
- `backend/src/query_translator.py` (614 lines)
- `backend/tests/test_query_translator.py` (686 lines)
- `backend/tests/test_translation_accuracy.py` (~300 lines)
- `frontend/components/search/language-selector.tsx` (103 lines)

**Files Modified:**
- `backend/src/ultimate_rag.py` — Translation integration
- `backend/src/query_enhancer.py` — Deprecation warning on `translate_for_bible()`
- `backend/src/comparative_rag.py` — Parallel translation
- `backend/src/llm_cache.py` — Cross-lingual cache metadata
- `backend/app/api/compare.py` — Response translation + `detected_language` field
- `backend/app/api/search.py` — `language` request field
- `backend/app/api/stream.py` — SSE language param + response translation
- `backend/tests/test_data.json` — 12 multilingual test cases added
- `backend/tests/run_retrieval_accuracy_test.py` — Stage 0 translation + native vs translated report
- `frontend/app/search/page.tsx` — LanguageSelector integration
- `frontend/app/compare/page.tsx` — LanguageSelector integration

**Git Commits (11):**
- `35d16b0` feat(backend): add QueryTranslator module with language detection and LLM translation
- `6287914` test(backend): add unit tests for QueryTranslator translate_query and translate_response
- `14934ab` feat(backend): integrate QueryTranslator into UltimateRAG search pipeline
- `05c1b21` feat(backend): integrate QueryTranslator into ComparativeRAG pipeline
- `e6142a4` feat(backend): add response translation for compare and search endpoints
- `cd8e957` feat(backend): add language parameter to search and compare API schemas
- `04f6050` feat(backend): optimize semantic cache for cross-lingual query hits
- `d799515` feat(frontend): add language selector component for multilingual search
- `7220661` feat(frontend): integrate language selector into search and compare pages
- `f3f1deb` test(backend): add translation accuracy tests with 40 multilingual query pairs
- (pending) docs: update project context for RFC-003 multilingual query translation

**Completed**:
- **Confidence Scoring Overhaul (2026-01-30)**: Implemented Two-Phase Sigmoid system. Scores now range 40-95%, accurately reflecting result quality.
- **Citation System Overhaul (2026-01-29)**: Replaced bracket-based citations with defense-in-depth architecture: backend sanitizer + rewritten parser + Radix HoverCard. Resolves Issue #16.
- **Landing Page Redesign (2026-01-29)**: Full marketing-ready overhaul of `frontend/app/page.tsx` for non-technical audience (theology/philosophy researchers). Utilitarian luxury design audit against Linear/Vercel/Raycast standards.
- **History Page Fix (2026-01-29)**: Complete overhaul of `/history` page — added `result_count` to SearchHistory model + DB migration, configured SDK client global auth, migrated from raw `fetch()` to generated SDK client, fixed search_type display with 13-value exhaustive mapping, updated tests to use SDK mocks.
- **History Page Test Update**: Replaced `global.fetch` mocking with SDK function mocks in `frontend/__tests__/history.test.tsx` and updated mock data to match the real API contract.
- **Advanced Logging System**: Implemented comprehensive structured logging for both frontend and backend with correlation ID tracking.
- **Streaming Format Fix (P0)**: Fixed critical SSE streaming format mismatch in compare endpoint. Essay paragraphs and statistics now display correctly.
- Reliability & Known Issues Fixes: Implemented circuit breakers, retry logic, SSE improvements, and offline handling.
- Test Coverage Improvements: Added 142 new tests across frontend and backend, achieving high coverage for critical reliability features.
- Sentry Observability Documentation: Documented environment variables and setup for Sentry in backend, frontend, and technical context.

### Landing Page Redesign (2026-01-29) - NEW

Full redesign of `frontend/app/page.tsx` to marketing-ready, utilitarian luxury standard for non-technical audience (theology/philosophy researchers, religious studies scholars).

**Design Principles Applied:**
- **Utilitarian luxury** (Linear/Vercel/Raycast style): restraint, whitespace, precision over persuasion
- **Non-technical language**: No "semantic search", "multi-agent analysis", "vector dimensions"
- **Neutrality**: No mezhep/denomination affiliation — every agent presents the text itself
- **Centered symmetry**: All card content, icons, text centered and height-aligned

**Sections Added:**
- **Multi-Agent Analysis Showcase** — 4 color-coded specialist agent cards (emerald/amber/sky/purple) + convergence visual + Synthesis Agent card with output tags
- **CTA Section** — Linear-style radial glow, gradient headline ("Start exploring sacred texts"), button with blur glow shadow, no card container

**Sections Redesigned:**
- **Features ("Why Clarus")** — Rewritten for humanities audience: "Understands What You Mean", "Every Scripture at Once", "Traceable to the Source" with tech footnotes at bottom
- **How It Works ("From Question to Insight")** — Steps renamed Ask→Enrich→Discover→Understand, all descriptions non-technical, centered card content
- **Hero** — Logo reduced 180→110px, bounce animation removed (restraint), subheadline rewritten to remove jargon
- **Footer** — Stripped from 4-column heavy (stats cards, trust badges, scripture sources) to minimal 2-row: logo+nav → copyright

**Sections Removed (redundant):**
- "What's Inside" Sources section (same data as agent cards)
- Stats Bar (43,055 / 4 / 5 — already communicated elsewhere)
- "Running in parallel" animated badge (dev monitoring aesthetic)

**Agent Card Text (Neutrality):**
- "Islamic Scholar" → "Quran Specialist"
- "classical Islamic tafsir tradition" → "the Quran's own words on any topic"
- "Judeo-Christian exegetical lens" → "the scripture in its own voice"
- "Christological perspective" → "the text as it was written"

**Cleanup:**
- Removed unused imports: `Zap`, `GlowCard`, `Database`
- Removed unused `sources` data array
- All builds pass clean

**File Modified:** `frontend/app/page.tsx` (single file, ~940 lines → ~850 lines)

### Advanced Logging System (2026-01-28) - NEW

Implemented industry-standard structured logging for full observability across the stack.

**Backend (Python):**
- `backend/app/logging_config.py` - Core logging module with:
  - `JSONFormatter` for production (machine-parseable)
  - `ConsoleFormatter` for development (colored, human-readable)
  - `RequestContextFilter` for automatic context injection
  - Context vars: `request_id`, `correlation_id`, `user_id`
  - `log_performance()` helper for latency tracking
  - `LogContext` context manager for scoped logging

- Integrated into all modules:
  - `app/main.py` - Startup logging with config info
  - `app/middleware/error_handler.py` - Structured error logging
  - `app/middleware/correlation.py` - NEW: Correlation ID middleware
  - `app/api/search.py`, `app/api/compare.py` - Request/response logging
  - `src/ultimate_rag.py`, `src/search.py` - Pipeline stage logging
  - `src/query_enhancer.py`, `src/answer_generator.py` - LLM call logging
  - `src/multi_agent_answer_generator.py` - Agent execution logging

**Frontend (TypeScript):**
- `frontend/lib/logger.ts` - Singleton Logger class with:
  - Log levels: DEBUG, INFO, WARN, ERROR
  - Sentry integration (errors auto-captured)
  - Correlation ID support
  - `useLogger()` hook for React components
  - `logPerformance()` helper

- `frontend/lib/correlation.ts` - Correlation ID utilities:
  - `startCorrelation()`, `endCorrelation()`
  - `getCorrelationHeaders()` for API requests

- Integrated into:
  - `lib/api-provider.tsx` - API error logging
  - `lib/auth/auth-context.tsx` - Auth flow logging
  - `components/error-boundary.tsx` - Error boundary logging
  - `app/search/page.tsx`, `app/compare/page.tsx` - Page logging

**Configuration:**
```bash
# Backend
LOG_LEVEL=INFO|DEBUG|WARNING|ERROR|CRITICAL
LOG_FORMAT=console|json
LOG_FILE=/path/to/file.log  # Optional

# Frontend
NEXT_PUBLIC_LOG_LEVEL=debug|info|warn|error
```

**Documentation:**
- `backend/LOGGING.md` - Backend logging guide
- `frontend/LOGGING.md` - Frontend logging guide
- `memory-bank/techContext.md` - Updated with logging architecture
- `CLAUDE.md` - Updated with logging configuration

### History Page Fix (2026-01-29) - NEW

Fixed all 6 bugs in the `/history` page and modernized the API integration.

**Backend Changes:**
- Added `result_count: Mapped[Optional[int]]` column to `SearchHistory` model (`backend/app/models.py`)
- Created idempotent migration script (`backend/scripts/add_result_count.py`)
- All 6 `SearchHistory` save points now include `result_count`:
  - `search.py`: `search_quran` (len results), `search_bible_{testament}` (len results)
  - `compare.py`: `compare_multi_agent` (total_verses), `compare` (total_citations)
  - `stream.py`: `stream_search_{source}` (None), `stream_compare` (None)
- `GET /history` response includes `result_count` in each item
- HistoryItem schema: `result_count: Optional[int] = None`

**Frontend Changes:**
- Created `frontend/lib/api/config.ts` — SDK client global auth configuration
  - `configureApiClient()` called at module scope in `layout.tsx`
  - Auto-injects `Authorization: Bearer <token>` via `client.setConfig({ auth: ... })`
  - SSR-safe: `typeof window` check for localStorage
- Migrated `/history` page from raw `fetch()` to SDK client:
  - `getSearchHistoryApiSearchHistoryGet` for listing
  - `deleteHistoryItemApiSearchHistoryHistoryIdDelete` for single delete
  - `clearHistoryApiSearchHistoryDelete` for clear all
- Fixed response parsing: `response.data.data` (items) + `response.data.pagination`
- Added exhaustive `SEARCH_TYPE_LABELS` map (13 values) with `getSearchTypeLabel()` helper
- Updated `result_count` display: null-safe, singular/plural

**Test Updates:**
- Replaced `global.fetch` mocking with `vi.mock('@/lib/api/sdk.gen')`
- Mock data uses real `search_type` values (`search_quran`, `search_bible_ot`)
- All 7 tests pass

**6 Bugs Fixed:**
1. Data key mismatch (`data.items` → `response.data.data`)
2. Pagination format mismatch (`per_page` → `limit`, `total` → `total_items`)
3. Query param mismatch (`per_page=20` → `limit=20`)
4. `result_count` missing → new column + null-safe display
5. `search_type` display broken → 13-value exhaustive mapping
6. Hardcoded `localhost:8000` → SDK client with global auth

**Git Commits (6):**
- `495dc0d` feat(backend): add result_count to SearchHistory model and API response
- `8fb5d26` feat(backend): add result_count database migration script
- `6722fc5` fix(frontend): configure SDK client global auth via @hey-api setConfig
- `a3568aa` fix(frontend): migrate history page from raw fetch to SDK client
- `d9bd662` fix(frontend): add exhaustive search_type display mapping for history page
- `957bcdc` test(frontend): update history tests to match real API contract and SDK client

### History Re-run Search — RFC-001 (2026-01-29) - NEW

Implemented RFC-001: Clicking history cards navigates to the appropriate search/compare page with the query pre-filled and auto-executed.

**Frontend Changes (3 files):**
- `frontend/app/history/page.tsx` — Added `getHistoryItemUrl()` mapping all 13 `search_type` values to URLs, `handleHistoryClick()` with `router.push()`, `cursor-pointer` on cards, `e.stopPropagation()` on delete button
- `frontend/app/search/page.tsx` — Added `queryOverride` parameter to `performBatchSearch`, `hasAutoExecuted` ref, auto-trigger `useEffect` reading `q` URL param
- `frontend/app/compare/page.tsx` — Added `Suspense` wrapper (renamed `ComparePage` → `CompareContent`), `useSearchParams` hook, `hasAutoExecuted` ref + auto-trigger `useEffect`

**Tests Added (12 new):**
- `history.test.tsx` — 5 tests (routing, compare routing, stopPropagation, special chars, fallback)
- `search-page.test.tsx` — 4 tests (auto-execute, empty q, absent q, source tab)
- `compare-page.test.tsx` — 3 tests (auto-execute, empty q, absent q)

**Pre-existing Test Fixes:**
- Fixed score assertion in "performs batch search" test (`"Score: 95.0%"` → `"95.0%"`)
- Removed obsolete "handles logout" test (button no longer rendered after UI redesign)

**Git Commits (5):**
- `4060329` feat(frontend): add clickable history cards with search_type routing
- `20e41a9` feat(frontend): add q URL param auto-search on search page
- `0e746d8` feat(frontend): add Suspense wrapper and q URL param auto-compare on compare page
- `89c5d4c` test(frontend): add tests for history re-run search feature
- `18cb5ff` fix(frontend): fix 2 pre-existing failing tests in search-page.test.tsx

### RFC-002: History Result Snapshots (2026-01-29) - DEFERRED

Created `docs/rfcs/002-history-result-snapshots.md` documenting the future possibility of storing search result snapshots in the database. Currently, clicking history re-runs the search. The RFC proposes adding a `snapshot` JSON column to `SearchHistory` for instant result recall. **Decision: Deferred** — semantic cache handles most repeat queries.

### Streaming Format Fix (2026-01-28) - CRITICAL

Fixed P0 blocker preventing essay display in compare page.

**Root Cause:**
- Backend sent word-by-word tokens: `{token: "word "}`
- Frontend expected structured messages: `{type: "paragraph", data: {...}}`
- Result: 100% message loss → empty essay display

**Solution:**
- Changed backend to send structured paragraph messages
- Fixed stats message format with all required fields
- Removed 15 print() statements (CLAUDE.md compliance)
- Added type hints and improved logging

**Files Modified:**
- `backend/app/api/stream.py` (~70 lines changed)

**Test Results:**
```
🎉 E2E TEST PASSED: All critical issues resolved!
✅ Issue #1: 5 paragraphs displayed
✅ Issue #2: Statistics showing correct values
✅ Verse cards rendered
✅ Filters functional
✅ Citations clickable
```

**Git Commits (6):**
- `dd7153a` fix(stream): fix SSE streaming format for compare endpoint
- `a28d95d` test(e2e): add Playwright E2E test suite for compare functionality
- `fd68a9e` docs: add implementation summary and test preparation guide
- `0732c9a` chore: update .gitignore for Playwright and Node.js artifacts
- `d66719f` docs: add test reports for streaming format fix
- `b557c24` fix(frontend): suppress hydration warning in Next.js layout

**GitHub Issues Created:**
- [#10](https://github.com/aliozdenisik/Clarus/issues/10) - DRY Violation: Verse Detail Extraction
- [#11](https://github.com/aliozdenisik/Clarus/issues/11) - DRY Violation: Paragraph Building
- [#12](https://github.com/aliozdenisik/Clarus/issues/12) - Playwright Test Timing Issues
- [#13](https://github.com/aliozdenisik/Clarus/issues/13) - Parent Epic: Post-Deployment Cleanup

### Sentry Comprehensive Observability Implementation (2026-01-27)

Full-stack Sentry observability implementation with end-to-end tracing, custom metrics, and production-ready alerts.

**Backend Instrumentation:**
- SqlAlchemy integration for DB query tracing
- LLM spans: query_enhancer, answer_generator, comparative, multi-agent
- Embedding spans: single and batch operations
- Circuit breaker events: Warning capture on OPEN state
- PII scrubbing: user data and LLM responses redacted

**Frontend Instrumentation:**
- Global Error Boundary with Sentry capture and fallback UI
- SSE error capture (parse, connection, init errors)
- API mutation global error handler
- User context (ID only, no PII)

**Custom Metrics:**
- RAG pipeline: enhance_latency, multi_latency, search_latency, cache_hit
- LLM cost tracking: tokens.input, tokens.output, cost.estimated

**Operational:**
- Chaos test script (`scripts/chaos_sentry_test.py`)
- RUNBOOKS.md with alert response procedures
- Alert rules documented (configure in Sentry UI)

**Files Created:**
- `frontend/components/error-boundary.tsx`
- `backend/scripts/chaos_sentry_test.py`
- `backend/RUNBOOKS.md`

**Files Modified (15+):**
- Backend: app/main.py, query_enhancer.py, answer_generator.py, comparative_answer_generator.py, multi_agent_answer_generator.py, embeddings.py, circuit_breaker.py, ultimate_rag.py, comparative_rag.py, test_sentry.py
- Frontend: providers.tsx, use-sse.ts, auth-context.tsx, api-provider.tsx, compare/page.tsx

### Reliability & Known Issues Fixes (2026-01-27)

Implemented comprehensive reliability improvements addressing 6 critical issues:

**Backend Improvements:**
- **Circuit Breaker Pattern** (pybreaker): Protects against Qdrant and OpenRouter failures
  - `qdrant_breaker`: fail_max=5, reset_timeout=60s
  - `llm_breaker`: fail_max=3, reset_timeout=30s
  - `embeddings_breaker`: fail_max=10, reset_timeout=120s
- **Tenacity Retry Decorators**: Exponential backoff on LLM calls (3 attempts, 2s→4s→8s)
- **Enhanced Health Check**: `/api/health` now returns event_loop status and Qdrant connectivity
- **Graceful Shutdown**: Proper cleanup in lifespan manager (5s timeout for DB/tasks)
- **SSE Heartbeats**: 4 heartbeat points in stream.py to prevent connection drops
- **systemd Service**: Template and install script at `backend/scripts/`

**Frontend Improvements:**
- **SSE Reconnection**: 3 retries with exponential backoff (1s→2s→4s)
- **Auth Timeout**: 10s AbortController timeout on auth check
- **Offline Banner**: Red banner when backend is unreachable
- **backendStatus State**: 'online' | 'offline' | 'unknown' in AuthContext

**New Files:**
- `backend/src/circuit_breaker.py` - Circuit breaker module
- `backend/scripts/systemd-install.sh` - Service installer
- `backend/scripts/clarus-backend.service.template` - Service template
- `frontend/components/layout/offline-banner.tsx` - Offline banner component

**Modified Files (14 total):**
- Backend: search.py, ultimate_rag.py, comparative_rag.py, query_enhancer.py, answer_generator.py, multi_agent_answer_generator.py, comparative_answer_generator.py, embeddings.py, app/main.py, app/api/stream.py
- Frontend: use-sse.ts, auth-context.tsx, providers.tsx

**Playwright Tests Verified:**
- Health check API: ✅ Returns healthy/degraded/unhealthy status
- SSE streaming: ✅ 80 verses returned across 4 sources
- Offline banner: ✅ Appears within 10s when backend down
- Online recovery: ✅ Banner disappears when backend restored

### Test Coverage Improvements (2026-01-27)
- Added 142 new tests (56 frontend, 76 backend unit tests, 10 extended auth tests).
- Verified reliability features: circuit breakers, health endpoints, and SSE reconnection.
- **Note**: Some pre-existing frontend tests are still failing. Refer to `ISSUES.md` for details on known test failures and resolution status.

## Recent Changes

### Google OAuth Integration (2026-01-26)

Frontend `AuthContext` updated to support Google OAuth login:

**Changes:**
- Added `loginWithGoogle(credential: string)` to `AuthContextType`.
- Implemented `loginWithGoogle` in `AuthProvider` using TDD.
- Function exchanges Google ID token for JWT via `/api/auth/google`.
- Tokens are stored in `localStorage` and `user` state is updated.
- Comprehensive error handling for network and backend errors.

**Test Results:**
- 5 new test cases added to `frontend/__tests__/auth-context.test.tsx`.
- All tests passed.

### Arabic Font Fix (2026-01-26)

Kuran ayetleri sayfasındaki bozuk Arapça görüntüleme düzeltildi:

**Problem:**
- Arapça harfler birleşmiyor, izole görünüyordu
- Harekeler (fatha, kasra, sukun) yanlış konumluydu
- Eksik glyph kutuları (□) görünüyordu
- Türkçe meal gösterilmiyordu

**Çözüm:**
- **Amiri** fontu eklendi (Google Fonts - klasik Arap kaligrafi tarzı)
- `.font-arabic` CSS sınıfı tanımlandı (RTL, line-height: 2)
- Türkçe çeviri her ayetin altında gösteriliyor
- Ayet numaraları büyütüldü (48px daire, 20px font)

**Değişen Dosyalar:**
- `frontend/app/layout.tsx` - Amiri font import
- `frontend/app/globals.css` - `.font-arabic` class
- `frontend/app/quran/[surahId]/page.tsx` - Verse interface + rendering

**Stil Değerleri:**
| Öğe | Değer |
|-----|-------|
| Arapça font | Amiri (Google Fonts) |
| Arapça boyut | `text-2xl` (24px) |
| Türkçe boyut | `text-2xl` (24px) |
| Türkçe renk | `--color-text-secondary` (#a1a1aa) |
| Ayet numarası | `h-12 w-12` daire, `text-xl` font |
| Satır aralığı | `line-height: 2` (harekeler için) |

**Commits:**
- `fix(frontend): add Arabic font support with Scheherazade New`
- `feat(frontend): display Turkish translation below Arabic verses`
- `style(frontend): increase translation and verse number sizes for better readability`
- `style(frontend): switch Arabic font from Scheherazade New to Amiri`

### Browse Detail Pages (2026-01-26)

Browse sayfalarından kitap/sure tıklandığında içerik görüntüleme sayfaları eklendi:

**Yeni Sayfalar:**
- `/quran/[surahId]/page.tsx` - Sure detay sayfası (Arapça ayetler)
- `/bible/[bookNr]/page.tsx` - Kitap detay sayfası (chapter seçimi + İngilizce ayetler)

**Özellikler:**
- **Quran Detay**: Sure başlığı (Arapça + transliterasyon), ayet listesi, "Back to Quran" navigasyon
- **Bible Detay**: Kitap başlığı, testament bilgisi, chapter seçim butonları, ayet listesi
- Chapter 1 otomatik yükleniyor
- Animasyonlu geçişler (Framer Motion)

**UI İyileştirmeleri:**
- `#67` gibi global kitap numaraları kaldırıldı (OT, NT, Apocrypha browse sayfalarından)
- Daha temiz kitap kartları (sadece isim + chapter sayısı)

**Düzenlenen Dosyalar:**
- `frontend/app/old-testament/page.tsx` - `#nr` kaldırıldı, `/bible/{nr}` yönlendirmesi
- `frontend/app/new-testament/page.tsx` - `#nr` kaldırıldı, `/bible/{nr}` yönlendirmesi
- `frontend/app/apocrypha/page.tsx` - `#nr` kaldırıldı, `/bible/{nr}` yönlendirmesi
- `frontend/app/quran/page.tsx` - `/quran/{id}` yönlendirmesi

**Backend API Kullanımı:**
- `GET /api/metadata/quran/surahs/{surah_id}` - Sure + ayetler
- `GET /api/metadata/bible/books/{book_nr}` - Kitap + chapter özeti
- `GET /api/metadata/bible/books/{book_nr}/chapters/{chapter_nr}` - Chapter + ayetler

**Test Sonuçları:**
- Quran: Al-Fatihah → 7 Arapça ayet ✅
- Bible: Genesis → Chapter 1 → 31 ayet ✅
- Console hatası yok ✅

### Compare Page Reference Enhancement (2026-01-26)

Compare sayfasına zengin kaynak referansları ve interaktif alıntılar eklendi:

**Backend Değişiklikleri:**
- `VerseDetail` Pydantic modeli eklendi (text, book_name, chapter, verse, source, translation)
- `verse_details: Optional[Dict[str, VerseDetail]]` field'ı CompareResponse'a eklendi
- `extract_quran_verse_detail()` ve `extract_bible_verse_detail()` helper fonksiyonları
- API response boyutu: 28KB (100KB limitinin altında)

**Frontend Bileşenleri (TDD ile):**
- `SourceBadge` - Kaynak renk badge'i (Kuran: Emerald, Eski Ahit: Blue, Yeni Ahit: Amber, Apokrifa: Purple)
- `SourceReferenceCard` - Ayet detayları kartı (badge + referans + çeviri + metin)
- `FilterTabs` - Kaynak filtreleme sekmeleri (Tümü, Kuran, Eski Ahit, Yeni Ahit, Apokrifa)
- `InlineCitation` - Tıklanabilir paragraf içi alıntılar

**Yeni Özellikler:**
- Tam ayet metinleri kaynak kartlarında görünür
- Kaynaklara göre filtreleme (20 ayet/kaynak)
- Paragraf içi `[Bakara:153]` alıntılarına tıklayınca ilgili karta scroll + 2sn highlight
- Çeviri bilgisi: "Diyanet Isleri Baskanligi" (Kuran), "King James Version with Apocrypha" (İncil)

**Test Sonuçları:**
- 71 test geçti (13 test dosyası)
- E2E browser testi başarılı
- Konsol hatası yok

**Dosyalar:**
- `backend/app/api/compare.py` - VerseDetail schema + helper functions
- `frontend/components/compare/` - 4 yeni bileşen
- `frontend/lib/utils/parse-citations.ts` - Citation parsing utility
- `frontend/__tests__/` - 5 yeni test dosyası (35 test)

### Rebranding to Clarus (2026-01-25)

Project rebranded from "Sacred Texts Search" to "Clarus":

**Documentation:**
- README.md - Project title
- memory-bank/projectbrief.md - Project title
- memory-bank/productContext.md - UI references

**Frontend:**
- package.json - App name
- app/layout.tsx - Metadata title
- app/page.tsx - Landing page title
- components/layout/navigation.tsx - Logo text
- app/search/page.tsx - Page heading
- messages/en.json - i18n strings
- messages/tr.json - i18n strings

**Backend:**
- backend/src/__init__.py - Package comment
- backend/app/main.py - FastAPI title & description
- backend/main.py - CLI docstring & argparse description

### Frontend Development Complete (2026-01-24)

Next.js 15 + Framer Motion ile modern frontend tamamlandi:

**Sayfalar:**
- `/` - Landing page (Sign In / Get Started)
- `/login` - JWT authentication
- `/register` - User registration
- `/search` - Kuran semantic search
- `/compare` - Multi-agent karsilastirmali analiz (CLI ciktisi gibi)

**Ozellikler:**
- Linear-style dark theme design system
- Spring animations (Framer Motion)
- GlowCard components
- Real-time search results
- 5-paragraph structured analysis display
- Citations badges per source
- Responsive layout

**Browser Test Results:**
- Login/Register: ✅ Calisiyor
- Search: ✅ 10 sonuc, skorlarla gosterim
- Compare: ✅ 80 verses → 5 paragraphs → 32 citations → %95 confidence

### User Preferences Page (2026-01-25)

- Implemented `/settings` with Zustand store integration
- Full form support for all 7 preference fields
- Validated with TDD (5 tests passing)

### Apocrypha Browse Page (2026-01-25)

- Implemented `/apocrypha` with book listing and filtering
- Copied pattern from Old Testament page
- Validated with TDD (4 tests passing)

### Backend Compare API Fix (2026-01-24)

`MultiAgentAnswer` serialization hatasi duzeltildi:

**Onceki (Hatali):**
```python
analysis=result.full_text if hasattr(result, 'full_text') else str(result)
```

**Sonraki (Dogru):**
```python
essay=result.to_essay()
paragraphs=[ParagraphData(...) for each commentary]
citations=result.citations
```

**Yeni CompareResponse Schema:**
```python
class CompareResponse:
    topic: str
    essay: str                      # Full markdown essay
    paragraphs: List[ParagraphData] # 5 structured paragraphs
    citations: Dict[str, List[str]] # Grouped by source
    confidence: float
    total_verses: int
    total_citations: int
    latency_ms: int
```

### Qdrant Persistence Fix (2026-01-25)

- **Root Cause**: Docker Desktop 4.55.0 bind mount sync issue
- **Solution**: Switched from bind mount (`./qdrant_data`) to named volume (`qdrant_storage`)
- **Verification**: All 43,055 vectors preserved across restart
- **Collections**: quran_tr (6,236), bible_ot (23,145), bible_nt (7,957), bible_apocrypha (5,717)

### New/Modified Files
- `frontend/app/compare/page.tsx` - Compare sayfasi (yeni)
- `frontend/app/search/page.tsx` - Compare butonu eklendi
- `backend/app/api/compare.py` - Rich response schema
- `test-credentials.json` - Browser test kullanicisi
- `.gitignore` - test-credentials.json eklendi

### Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15 + Framer Motion |
| CLI | argparse + Rich |
| Backend | FastAPI + SQLAlchemy |
| Auth | JWT + Google OAuth |
| Database | PostgreSQL |
| Vector DB | Qdrant |

### Testament Collections

| Collection | Points | Agent |
|------------|--------|-------|
| `quran_tr` | 6,236 | QuranAgent |
| `bible_ot` | 23,145 | OldTestamentAgent |
| `bible_nt` | 7,957 | NewTestamentAgent |
| `bible_apocrypha` | 5,717 | ApocryphaAgent |

## Next Steps

### 🔴 SECURITY FIXES (CRITICAL - BEFORE PRODUCTION)

1. **Immediate (Today)**
   - Rotate all exposed credentials (OpenRouter, Google OAuth, JWT secret)
   - Remove `.env` from git history
   - Disable debug mode in production

2. **Urgent (This Week)**
   - #39-#44: Fix all CRITICAL security issues
   - Add authentication to keyword_search and metadata endpoints
   - Remove JWT token from query parameters
   - Add security headers middleware
   - Fix CORS configuration

3. **High Priority (This Sprint)**
   - #45-#47: Fix all HIGH security issues
   - Migrate tokens from localStorage to HttpOnly cookies
   - Add CSRF protection
   - Implement rate limiting on auth endpoints
   - Fix SQL injection anti-pattern in morphology search
   - Fix XSS sanitization

4. **Medium Priority (Next Sprint)**
   - #48-#49: Fix MEDIUM/LOW security issues
   - Add password complexity validation
   - Implement account lockout
   - Hash refresh tokens
   - Add comprehensive audit logging

### Post-Security Cleanup (GitHub Issues)

5. **Feature Issues**
   - #22 (RFC-005 Save/Share)
   - #24 (Markdown bug in Compare UI)
   - #12: Fix Playwright E2E test timing issues
   - #10: Refactor verse detail extraction (DRY)
   - #11: Refactor paragraph building (DRY)

6. **Production Readiness**
   - Docker production build
   - HTTPS configuration
   - Google OAuth credentials setup (after rotating current ones)

4. **Frontend Enhancements**
   - ~~Bible search page~~ ✅
   - ~~User preferences page~~ ✅
   - ~~Search history page~~ ✅ (Fixed 2026-01-29)

5. **Optional Enhancements**
   - Arabic font optimization
   - Batch query API
   - WebSocket support for real-time chat
   - History result snapshots (RFC-002 — deferred)

## Security Tracking

### CVE-2026-0994 - Protobuf JSON Recursion DoS (2026-01-27)

| Field | Value |
|-------|-------|
| **CVE** | CVE-2026-0994 |
| **CVSS** | 8.6 HIGH |
| **Affected** | protobuf ≤6.33.4 (installed: 6.33.2) |
| **Patched** | None yet |
| **Risk** | LOW - Not exploitable in Clarus |

**Assessment**: Vulnerability is in `json_format.ParseDict()`. Clarus uses protobuf only for internal gRPC (qdrant-client) and ONNX inference (fastembed) - neither accepts untrusted JSON input. No exposed attack surface.

**Tracking**:
- PR: https://github.com/protocolbuffers/protobuf/pull/25239
- Comment added to `backend/requirements.txt`

**Action**: Upgrade protobuf when patch is released.

## Active Decisions

- **Rate Limit**: 50 queries/day/user
- **Language**: Turkish (Quran), English (Bible)
- **Primary Interface**: Web App + CLI
- **Frontend Framework**: Next.js 15 (App Router)

## Test Credentials

Browser testleri icin kullanilir (`.gitignore`'da):
```json
{
  "email": "browser-test@example.com",
  "password": "Test1234!",
  "name": "Browser Test"
}
```

## Learnings

1. **Next.js 15** App Router + Framer Motion iyi calisiyor
2. **FastAPI + SQLAlchemy async** handles concurrent requests efficiently
3. **SSE streaming** provides good UX for long-running LLM calls
4. **Semantic LLM Cache** significantly reduces API costs (60-80%)
5. **MultiAgentAnswer.to_essay()** metodu API serialization icin kullanilmali
6. **Structured logging** with correlation IDs enables end-to-end request tracing
7. **Context vars** (Python) and singletons (TS) enable clean context propagation
