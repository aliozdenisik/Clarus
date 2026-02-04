# Issue #005: Align Compare Page UI with Search Page Standards

**Status:** Open  
**Priority:** Medium  
**Date Reported:** 2026-01-29  
**Component:** Frontend / Compare Page (`frontend/app/compare/page.tsx`)

---

## Problem Description

The Search page UI has been updated to industry standards with improved typography, colors, and AI output presentation. The Compare page needs to be updated to match this new design language to ensure consistency across the application.

## Observed Behavior (Compare Page)

- Standard blue buttons.
- Default font weights and sizes.
- Missing "AI INTERPRETATION" stylistic header.
- Standard link styling for citations.

## Expected Behavior (Match Search Page)

### Typography
- Adopt the font family, weights, and sizes used in the Search page.

### Color Palette
- Use the specific teal/cyan accent color from the Search page for buttons and active elements.

### AI Output Styling
- Implement the "AI INTERPRETATION" label style (small caps, tracking, vertical left border) for the agent outputs.

### Citation Styling
- Match the dotted underline style for inline citations.

### Spacing
- Ensure consistent padding and margins around result blocks.

## Affected Files

- `frontend/app/compare/page.tsx`
- `frontend/components/compare/*.tsx` (source badge, citation components)
- `frontend/styles/globals.css` or Tailwind config

## Design Tokens to Match

| Element | Search Page Style | Compare Page Current |
|---------|-------------------|---------------------|
| **Primary Button** | Teal/cyan gradient | Standard blue |
| **AI Header** | "AI INTERPRETATION" (small caps, border) | Missing |
| **Citations** | Dotted underline, hover effect | Standard link |
| **Font Weight** | Bold headings, regular body | Mixed |
| **Spacing** | Consistent 8px grid | Inconsistent |

## Implementation Checklist

- [ ] Update button colors to match Search page accent color
- [ ] Add "AI INTERPRETATION" styled header to agent outputs
- [ ] Apply dotted underline citation styling
- [ ] Standardize typography (font family, weights, sizes)
- [ ] Normalize spacing/padding to match Search page
- [ ] Add any missing Framer Motion animations (if used on Search page)

## Related Issues

- None

## Notes

- Consider extracting shared UI components (e.g., `<AIOutputHeader>`, `<CitationLink>`) to ensure consistency and reduce duplication.
- Reference the Search page implementation as the source of truth for design standards.
