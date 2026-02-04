# Issue: In-text Citation Hover Missing on Compare Page

**Created:** 2026-01-29
**Status:** Open
**Priority:** Medium
**Category:** UI/UX Bug

---

## Problem

When clicking an in-text citation in the compare page text, the system correctly:
- ✅ Highlights the referenced verse card
- ✅ Scrolls to the verse
- ✅ Opens the verse in a new tab

However, it **does NOT**:
- ❌ Display the hover tooltip/popover that shows verse preview
- ❌ Auto-trigger the hover effect on the verse card

This differs from the **search page**, where citations work correctly with tooltip preview.

---

## Root Cause

**Search Page** (working):
- Citations wrapped with `<VerseTooltip>` component
- Controlled `isOpen` state triggers tooltip on click
- File: `frontend/app/search/page.tsx` lines 396-419

**Compare Page** (broken):
- Citations rendered standalone without `VerseTooltip` wrapper
- File: `frontend/app/compare/page.tsx` lines 603-608

---

## Expected Behavior

Clicking an in-text citation should:
1. Scroll to the referenced verse card
2. Highlight the verse card (currently working)
3. **Auto-open the hover tooltip/popover** showing verse preview (MISSING)
4. Optionally open verse page in new tab (currently working)

---

## Technical Details

### Search Page Pattern (Correct)
```typescript
// frontend/app/search/page.tsx:396-419
<VerseTooltip
  reference={part.reference}
  verseDetail={verse}
  onNavigate={navigateToVerse}
  isOpen={openPopover === part.reference}
  onOpenChange={(open) => setOpenPopover(open ? part.reference : null)}
>
  <InlineCitation 
    reference={part.reference} 
    onClick={() => navigateToVerse(part.reference)} 
  />
</VerseTooltip>
```

### Compare Page Pattern (Broken)
```typescript
// frontend/app/compare/page.tsx:603-608
<InlineCitation
  reference={part.reference}
  onClick={() => navigateToVerse(part.reference)}
/>
```

---

## Proposed Solution

### Option A: Add VerseTooltip Wrapper (Recommended)
Wrap citations with `VerseTooltip` component to match search page behavior:

1. Add `openPopover` state to `CompareContent` component
2. Wrap `InlineCitation` with `VerseTooltip` (lines 603-608)
3. Pass controlled `isOpen` and `onOpenChange` props

### Option B: Scroll + Auto-Trigger Hover State
Modify `scrollToVerse` to trigger synthetic hover event on verse card element.

---

## Files Affected

- `frontend/app/compare/page.tsx` - Compare page main component
- `frontend/components/compare/inline-citation.tsx` - Citation component (shared)
- `frontend/components/search/verse-tooltip.tsx` - Tooltip component (import needed)
- `frontend/components/compare/source-reference-card.tsx` - Verse card (might need hover state)

---

## Acceptance Criteria

- [ ] Clicking citation in compare page auto-opens tooltip preview
- [ ] Tooltip positioning matches search page behavior
- [ ] Verse card highlight + scroll still works
- [ ] Navigation to verse page in new tab still works
- [ ] Tooltip closes when clicking another citation or outside

---

## Related Components

- `InlineCitation` - Clickable citation link
- `VerseTooltip` - Radix Popover showing verse preview
- `SourceReferenceCard` - Verse card with highlight effect
- `scrollToVerse()` - Scroll + highlight logic
- `navigateToVerse()` - Opens verse page in new tab
