
## Task 10b: New Testament Browse Page (2026-01-25)

### Implementation Details
- **Created**: `frontend/app/new-testament/page.tsx`
- **Created**: `frontend/__tests__/new-testament.test.tsx` (TDD first)
- **Features**:
  - Displays 27 NT books with chapter counts
  - Filter by English or Greek names (Transliterated)
  - Client-side Greek name mapping implemented
  - Click navigates to `/search?source=nt&book={nr}`
  - Protected route using `useAuth` hook

### Key Design Decisions
1. **Greek Mapping**:
   - Followed the Old Testament pattern of providing secondary names.
   - Added `GREEK_NAMES` map for all 27 books (e.g., "Matthew" -> "Kata Matthaion").
   - Filter searches both English and Greek names.

2. **Reuse of OT Patterns**:
   - Copied structure from `OldTestamentPage` exactly as requested.
   - Maintained consistency in animations (`springPresets`) and UI components (`GlowCard`, `Input`, `motion.div`).

### Verification
- `npm test -- --run new-testament` passed (4 tests).
- `npm run build` passed successfully.

## Task 11: Apocrypha Browse Page (2026-01-25)

### Implementation Details
- **Created**: `frontend/app/apocrypha/page.tsx`
- **Created**: `frontend/__tests__/apocrypha.test.tsx` (TDD first)
- **Features**:
  - Displays ~15 Apocrypha books (dynamic based on API)
  - Filter by English names
  - Click navigates to `/search?source=apocrypha&book={nr}`
  - Protected route using `useAuth` hook

### Key Design Decisions
1. **Simplified Filtering**:
   - Removed Hebrew/Greek name mapping as it wasn't required/available for Apocrypha.
   - Kept the same filtering logic structure for consistency but only checks English names.

2. **Reuse of OT/NT Patterns**:
   - Exact copy of `OldTestamentPage` structure.
   - Consistent animations and UI.

### Verification
- `npm test -- --run apocrypha` passed (4 tests).
- `npm run build` passed successfully.
