# Issue #002: Comparative Analysis Stats Zeroed Out

**Status:** Open  
**Priority:** High  
**Date Reported:** 2026-01-29  
**Component:** Frontend / Compare Page (`frontend/app/compare/page.tsx`)

---

## Problem Description

In the Comparative Analysis results, the stats bar displays "0 verses", "0.0s", and "0% confidence" even when the analysis is complete and citations are found (e.g., "30 citations").

## Observed Behavior

- `total_citations` is correct (calculated client-side from paragraphs).
- `total_verses`, `latency_ms`, and `confidence` are **0**.

## Expected Behavior

All stats should display actual values:
- `total_verses`: Count of unique verses referenced
- `latency_ms`: Time taken for the analysis
- `confidence`: Confidence score from the backend

## Root Cause Analysis

These zeroed metrics depend on a `stats` event from the SSE stream. The `total_citations` is calculated derived from the received paragraphs. The discrepancy suggests the `stats` event is either:

1. **Not being sent by the backend.**
2. **Being sent but missed/overwritten** in the frontend state update logic in `useEffect`.
3. **Arriving with 0 values** from the backend.

## Affected Files

- `frontend/app/compare/page.tsx` (stats display + SSE handling)
- `backend/app/api/compare.py` (SSE stream generator)

## Debugging Steps

1. [ ] Add console logging to track all SSE events received by frontend
2. [ ] Add backend logging to confirm `stats` event is being sent
3. [ ] Verify the exact shape/content of the `stats` event payload
4. [ ] Check if state update logic overwrites stats before rendering

## Proposed Solutions

1. **If backend not sending:** Add `stats` event emission to the SSE stream
2. **If frontend losing data:** Fix state update logic to preserve stats across renders
3. **If timing issue:** Ensure stats event is sent before stream close

## Related Issues

- None

## Notes

- The `total_citations` working correctly proves the frontend can process and display stats, so the issue is specific to the `stats` event flow.
