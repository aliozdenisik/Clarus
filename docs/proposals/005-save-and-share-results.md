# RFC-005: Save & Share Search Results

**Status**: Proposed
**Created**: 2026-02-01
**Effort**: Medium

---

## Summary

Allow users to save search results and comparative analyses to a personal collection, and share them with others via a unique public link.

## Motivation

Currently, search results and multi-agent comparisons are ephemeral. Once a user leaves the page, the result is gone. The history page lets users re-run past queries, but this has two limitations:

1. **No instant recall** -- Re-running a query costs 2-40 seconds (depending on cache hit) and may produce slightly different LLM output each time.
2. **No sharing** -- A researcher who finds a compelling comparative analysis cannot send it to a colleague. The only option is a screenshot.

For the target audience (theology/philosophy researchers, religious studies scholars), the ability to curate and share findings is a core workflow need.

## Proposal

### Save to Collection

- A "Save" button appears on search result cards and at the top of comparative analysis essays.
- Clicking "Save" stores the full result (query, answer text, citations, verse details, confidence score, metadata) server-side, linked to the user's account.
- A new `/saved` page lists all saved items, grouped by type (Search / Compare).
- Users can delete saved items individually or in bulk.
- Saved items are immutable snapshots -- they do not change when the underlying data or models change.

### Share via Link

- Each saved item gets a unique, short public URL (e.g., `/s/abc123`).
- The share link opens a read-only view of the saved result, accessible without authentication.
- The read-only view shows the full result with the same styling as the original page (essay paragraphs, source cards, citations, confidence score).
- A "Copy Link" button next to each saved item makes sharing frictionless.
- Optionally, a shared result can be marked as "private" (only accessible by the owner).

### User Experience

1. User searches or runs a comparison.
2. User clicks "Save" on a result they find valuable.
3. Result appears in `/saved` with a shareable link.
4. User copies the link and sends it to a colleague.
5. Colleague opens the link and sees the full result without logging in.

## Expected Outcome

- Users can build a personal library of meaningful search results and analyses.
- Saved results load instantly (no re-computation, no LLM cost).
- Any result can be shared with a single link.
- Shared links are lightweight and load fast (static data, no LLM calls).
- Researchers can reference specific Clarus analyses in their work.

## Open Questions

1. **Expiration** -- Should shared links expire after a certain period, or persist indefinitely?
2. **Rate limit** -- Should there be a maximum number of saved items per user (e.g., 100)?
3. **Export** -- Should saved results be exportable as PDF or Markdown in this phase, or defer to a future RFC?
4. **Anonymous sharing** -- Should unauthenticated users be able to share results (via session-based temporary saves), or require login?
