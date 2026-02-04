# Issue #003: Inconsistent Search Navigation Options

**Status:** Open  
**Priority:** Low  
**Date Reported:** 2026-01-29  
**Component:** Frontend / Header Navigation

---

## Problem Description

The global header navigation under the "Search" dropdown only lists two options: "Quran Search" and "Bible Search". However, the actual Search page and application logic support four distinct collections/search modes: Quran (Kuran), Old Testament (Eski Ahit), New Testament (Yeni Ahit), and Apocrypha (Apokrifa).

## Observed Behavior

- **Header "Search" dropdown:** [Quran Search, Bible Search]
- **Search Page Tabs:** [Kuran, Eski Ahit, Yeni Ahit, Apokrifa]

## Expected Behavior

The global navigation should reflect the available search scopes. Options should be:

1. **Quran Search** → `/search?source=quran`
2. **Old Testament Search** → `/search?source=ot`
3. **New Testament Search** → `/search?source=nt`
4. **Apocrypha Search** → `/search?source=apocrypha`

OR keep the simplified 2-item dropdown but make it clear it groups collections.

## User Experience Impact

The discrepancy between the 2-item dropdown and the 4-item tab interface creates a disjointed user experience. Users may not discover the full search capabilities.

## Affected Files

- `frontend/components/header.tsx` (or navigation component)
- `frontend/app/search/page.tsx` (search page tabs)

## Proposed Solutions

1. **Option A (Explicit):** Expand the dropdown to 4 items matching the search page tabs
2. **Option B (Grouped):** Keep 2 items but add descriptive text like "Bible Search (OT, NT, Apocrypha)"
3. **Option C (Simplified):** Keep 2 items, rely on users discovering tabs on the search page

## Recommendation

**Option A** for clarity and discoverability.

## Related Issues

- #004 (Missing book count for Apocrypha)

## Notes

- None
