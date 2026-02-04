# Issue #004: Missing Book Count for Apocrypha in Navigation Menu

**Status:** Open  
**Priority:** Low  
**Date Reported:** 2026-01-29  
**Component:** Frontend / Navigation

---

## Problem Description

The "Apocrypha" item in the Browse/Compare dropdown menu is missing the book count (e.g., "(X Books)"), unlike the other items (Quran, Old Testament, New Testament) which display their counts.

## Observed Behavior

- Quran **(114 Surahs)**
- Old Testament **(39 Books)**
- New Testament **(27 Books)**
- Apocrypha ← **Missing count**

## Expected Behavior

- Apocrypha **(X Books)**

## Why This Matters

Consistency in UI presentation. The missing count makes the interface feel incomplete or suggests the Apocrypha data might be incomplete/unavailable.

## Affected Files

- `frontend/components/navigation.tsx` (or wherever the Browse/Compare dropdown is defined)

## Solution

1. Determine the correct book count for Apocrypha collection
2. Add the count to the navigation menu item

## Book Count Verification

According to the README:
- `bible_apocrypha`: **5,717 verses**
- Book count: **TBD** (needs to be queried from the data)

## Related Issues

- #003 (Inconsistent search navigation)

## Notes

- The actual book count should be verified from the `data/bible_kjva.json` file or the Qdrant collection metadata.
