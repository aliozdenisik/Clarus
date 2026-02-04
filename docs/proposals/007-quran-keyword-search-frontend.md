# RFC-007: Quran Keyword Search Frontend

**Status**: Proposed
**Created**: 2026-02-01
**Effort**: High

---

## Summary

Build a dedicated frontend interface for the Quran morphological keyword search feature, allowing users to explore Arabic root-based word relationships, see where words appear across surahs, and read verses containing those words — all through a premium, utilitarian luxury UI that matches the existing Clarus design language.

## Motivation

The backend morphological keyword search (RFC-006) is fully operational with 77,429 indexed words and 1,651 Arabic roots, but it is only accessible via CLI and raw API calls. Researchers and students of the Quran have no visual way to:

- Search for an Arabic root and see every derived word form in the Quran
- Understand the distribution of a concept across surahs at a glance
- Read verses in context with matched words visually highlighted
- Browse the full root catalogue and discover linguistic patterns
- Input queries in both Arabic script and Latin/Buckwalter transliteration

This is the most academically valuable feature in Clarus — a concordance tool — and it deserves a frontend experience that matches its depth.

## Proposal

### 1. New Dedicated Page: `/keyword-search`

A standalone page accessible from the main navigation under a new "Word Search" entry. The page should feel scholarly yet refined — like opening a beautifully typeset concordance, not a database query tool.

### 2. Search Experience

The user types an Arabic word (e.g., كتب) or its Latin/Buckwalter equivalent (e.g., "ktb") into a search input. The system identifies the root, shows how it was found (exact match, prefix stripped, algorithmic, or fuzzy), and displays:

- **Root Card**: The identified Arabic root in large calligraphic display (Amiri font), with the root detection method shown subtly below
- **Statistics Bar**: Total occurrences, number of unique derived words, number of surahs containing the root
- **Derived Words Cloud**: All unique word forms derived from this root, displayed as interactive tags the user can click to filter verses

### 3. Surah Distribution Visualization

A visual representation showing which surahs contain the root and how frequently. This could be a horizontal bar chart, a heat-map strip, or a proportional grid — whatever communicates distribution most clearly at a glance. Each surah entry should be clickable to filter the verse list below.

### 4. Verse Results

Paginated verse cards showing:
- Surah name and verse number
- Full Arabic text (Uthmani script) with matched words visually distinguished (highlighted, underlined, or colored)
- Clean Arabic text for accessibility
- Click-to-navigate to the full surah page (`/quran/[surahId]`)

Pagination should feel seamless — either infinite scroll or numbered pages matching the existing design language.

### 5. Root Browser

A secondary mode or companion section allowing users to browse all 1,651 roots sorted by frequency. Each root shown with its occurrence count, clickable to perform the search. This enables discovery — "What are the most frequent concepts in the Quran?"

### 6. Input Flexibility

The search input must support:
- Arabic script (كتب)
- Buckwalter transliteration (ktb)
- Arabic words with prefixes (الكتاب — the system strips prefixes automatically)

A small helper hint near the input should explain that both Arabic and Latin input are accepted.

### 7. Navigation Integration

Add "Word Search" to the main navigation bar, under the Search dropdown or as a standalone top-level item alongside Search and Compare. Mobile navigation must also include it.

### 8. Design Standards

The interface must follow the established Clarus utilitarian luxury principles:
- Dark theme (Zinc-950 base, Indigo-500 accents)
- Restrained animations (Framer Motion spring presets)
- Arabic text in Amiri font with proper RTL handling and line-height for diacritics
- No visual clutter — every element must earn its place
- Loading skeletons during search, toast notifications for errors
- Responsive layout: desktop and mobile

## Expected Outcome

- Users can search for any Arabic root or word and instantly see its Quranic footprint
- Surah distribution is visible at a glance without scrolling through hundreds of verses
- Matched words are visually highlighted in verse text, making pattern recognition effortless
- The root browser enables serendipitous discovery of linguistic patterns
- Both Arabic-literate and Latin-only users can access the feature equally
- The page feels like a natural extension of the existing Search and Compare experiences
- All API endpoints are connected via the generated SDK client (OpenAPI types regenerated)
- Navigation is updated across desktop and mobile

## Future Scope

This RFC covers the Quran keyword search frontend only. A future phase will extend the same word search interface to cover **Old Testament, New Testament, and Apocrypha** collections. The UI architecture should be designed with this expansion in mind — source tabs, collection-agnostic verse cards, and a flexible data model that can accommodate non-Arabic linguistic structures (e.g., Hebrew/Greek root systems or English lemmatization). Implementation details for Bible keyword search will be proposed in a separate RFC once the Quran frontend is validated.

## Open Questions

- Should the root browser be a separate tab within the page, or a collapsible sidebar panel?
- Should the surah distribution use a bar chart, heat-map, or another visualization format?
- Should verse cards show the Turkish translation alongside Arabic text, or keep it Arabic-only for this scholarly tool?
- Should there be a "Popular Roots" or "Featured Roots" section on the empty state before the user searches?
- What linguistic model should be used for Bible word search — Hebrew/Greek root morphology, English lemmatization, or both?
