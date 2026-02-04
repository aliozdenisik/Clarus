# RFC-002: History Result Snapshots

**Status**: Future
**Created**: 2026-01-29
**Effort**: High (3 layers: DB migration, backend API, frontend UI)

## Problem

The history system only stores query metadata (`query`, `search_type`, `result_count`, `timestamp`). When a user clicks a history item, the search is re-executed against the live database. This means:

- **No instant results** — Every history click costs 2-3s (cache hit) or 10-40s (cache miss / compare)
- **No result persistence** — If the semantic cache expires (7-day TTL), old results are lost forever
- **No reproducibility** — Re-indexing or embedding model changes alter results for the same query
- **API cost on miss** — Cache miss triggers full LLM pipeline (~$0.013/query)

## Current State

### What's Stored (`SearchHistory` model)

```python
class SearchHistory(Base):
    query: Mapped[str]              # "sabır ve namaz"
    search_type: Mapped[str]        # "search_quran", "compare", etc.
    result_count: Mapped[int]       # 12
    # Nothing else — no results, no LLM answer, no scores
```

### Current Flow

```
History card click → router.push(/search?q=...) → New API call → New results
```

## Proposed Solution: Store Result Snapshots

Save the full search response as a JSON snapshot alongside the history entry.

### Database Changes

Add a `snapshot` JSON column to `search_history`:

```python
class SearchHistory(Base):
    # ... existing fields ...
    snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Contains the full API response: results[], scores, LLM answer, etc.
```

Migration: `alembic revision --autogenerate -m "add snapshot to search_history"`

### Backend Changes

**Save snapshot** — In each search endpoint (`backend/app/api/search.py`, `backend/app/api/compare.py`), after computing the response, save it into the history entry:

```python
history_entry = SearchHistory(
    query=query,
    search_type="search_quran",
    result_count=len(results),
    snapshot=response.model_dump()  # NEW: full response as JSON
)
```

**New endpoint** — `GET /api/history/{id}/snapshot` returns the saved snapshot without re-running the search.

### Frontend Changes

**History page** — Two click behaviors:
1. **View saved results** (default) — Show snapshot inline or in a detail page
2. **Re-run search** — Existing behavior, available as secondary action (button)

**New route** — `/history/{id}` detail page showing the saved snapshot with the same UI as search results.

### Size Estimation

| Search Type | Avg Response Size | 1000 Searches |
|-------------|-------------------|---------------|
| `search_quran` | ~5-10 KB | ~5-10 MB |
| `compare` (multi-agent) | ~30-50 KB | ~30-50 MB |
| Mixed average | ~15 KB | ~15 MB |

With rate limit of 50 queries/day/user, growth is manageable.

### Trade-offs

| Aspect | Re-run (current) | Snapshot (proposed) |
|--------|-------------------|---------------------|
| Latency | 2-40s | Instant |
| Storage | 0 | ~15 KB/search |
| Freshness | Always current | Point-in-time |
| Cost | $0-0.013/click | $0 |
| Complexity | Simple | DB migration + new endpoint + new UI |
| Stale data | N/A | Results frozen at search time |

## Decision

**Deferred.** Current re-run behavior is acceptable — semantic cache handles most repeat queries efficiently. Revisit when:
- Users complain about history load times
- Compare queries (10-40s) are frequently re-accessed
- Offline/instant access becomes a requirement
