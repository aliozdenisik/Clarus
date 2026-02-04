# RFC-001: History Page Re-run Search

**Status**: Implemented
**Created**: 2026-01-29
**Implemented**: 2026-01-29
**Effort**: Medium

## Problem

History page displays past queries as static cards. Users cannot click an item to navigate back to its results. The page is effectively read-only with no actionable value beyond viewing past query text.

## Proposed Solution: Re-run Query

When a user clicks a history item, redirect to the appropriate page with the query pre-filled and auto-executed.

### Routing Logic

| `search_type` | Redirect |
|---|---|
| `search_quran`, `stream_search_quran` | `/search?source=quran&q={query}` |
| `search_bible_all`, `stream_search_bible` | `/search?source=ot&q={query}` |
| `search_bible_ot`, `stream_search_ot` | `/search?source=ot&q={query}` |
| `search_bible_nt`, `stream_search_nt` | `/search?source=nt&q={query}` |
| `search_bible_apocrypha`, `stream_search_apocrypha` | `/search?source=apocrypha&q={query}` |
| `compare`, `compare_multi_agent`, `stream_compare` | `/compare?q={query}` |

### Changes Required

**Frontend (`app/history/page.tsx`)**:
- Make history cards clickable (wrap in link or add onClick handler)
- Map `search_type` to target URL with `q` param

**Frontend (`app/search/page.tsx`)**:
- Read `q` param from `searchParams`
- Auto-populate input and trigger search on mount when `q` is present

**Frontend (`app/compare/page.tsx`)**:
- Read `q` param from `searchParams`
- Auto-populate input and trigger comparison on mount when `q` is present

**Backend**: No changes required.

### Why Re-run Instead of Caching Responses

| Approach | Pros | Cons |
|---|---|---|
| **Re-run** | Clean, no DB bloat, semantic cache handles repeat queries (~$0 cost) | 2-3s latency on cache miss |
| **Store response in DB** | Instant results | 10-50KB JSON per search, DB grows fast, migration needed, stale data risk |

Semantic cache (95% similarity, 7-day TTL) already handles repeat queries efficiently. Re-run is the pragmatic choice.

## Files to Modify

1. `frontend/app/history/page.tsx` — clickable cards + routing
2. `frontend/app/search/page.tsx` — `q` URL param support + auto-search
3. `frontend/app/compare/page.tsx` — `q` URL param support + auto-compare

## Implementation

**Commits (5):**
- `4060329` feat(frontend): add clickable history cards with search_type routing
- `20e41a9` feat(frontend): add q URL param auto-search on search page
- `0e746d8` feat(frontend): add Suspense wrapper and q URL param auto-compare on compare page
- `89c5d4c` test(frontend): add tests for history re-run search feature
- `18cb5ff` fix(frontend): fix 2 pre-existing failing tests in search-page.test.tsx

**Files Modified:**
- `frontend/app/history/page.tsx` — Clickable cards + `getHistoryItemUrl()` routing
- `frontend/app/search/page.tsx` — `q` URL param auto-search with `hasAutoExecuted` ref
- `frontend/app/compare/page.tsx` — Suspense wrapper + `q` URL param auto-compare
- `frontend/__tests__/history.test.tsx` — 5 new tests
- `frontend/__tests__/search-page.test.tsx` — 4 new tests + 2 pre-existing test fixes
- `frontend/__tests__/compare-page.test.tsx` — 3 new tests

**Test Results:** 178 tests passing across 19 test suites.
