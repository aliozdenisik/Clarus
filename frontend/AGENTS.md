# FRONTEND - KNOWLEDGE BASE

## OVERVIEW

Next.js 16 App Router with Framer Motion animations, Zustand state, and TanStack Query. Generated TypeScript API client from OpenAPI spec. Linear-style dark theme. 17 pages, 60+ components, 35 test files.

## STRUCTURE

```
frontend/
├── app/                        # App Router pages (17 files)
│   ├── layout.tsx              # Root layout + providers
│   ├── page.tsx                # Landing page
│   ├── global-error.tsx        # Global error boundary
│   ├── login/                  # Auth pages
│   ├── register/
│   ├── search/                 # Quran search
│   ├── compare/                # Multi-agent comparison (1070 lines)
│   ├── keyword-search/         # Morphological keyword search
│   ├── history/                # Search history
│   ├── settings/               # User preferences
│   ├── quran/                  # Quran browse (index + [surahId])
│   ├── bible/[bookNr]/         # Bible book browse
│   ├── old-testament/          # OT browse
│   ├── new-testament/          # NT browse
│   └── apocrypha/              # Apocrypha browse
├── components/
│   ├── ui/                     # Radix + library primitives (26 files)
│   ├── motion-primitives/      # Motion Primitives components (1 file)
│   ├── compare/                # Compare domain (7 files)
│   ├── keyword-search/         # Keyword search domain (12 files)
│   ├── verse-lookup/           # Verse lookup (2 files)
│   ├── search/                 # Search domain (4 files)
│   ├── layout/                 # Navigation, offline banner
│   ├── motion/                 # Framer Motion wrappers
│   ├── providers.tsx           # Root provider composition
│   └── error-boundary.tsx      # Error boundary component
├── lib/
│   ├── api/                    # Generated client (2054+ lines types)
│   │   ├── config.ts           # SDK client global auth configuration
│   │   ├── types.gen.ts        # TypeScript types from OpenAPI
│   │   ├── sdk.gen.ts          # API methods
│   │   ├── client.gen.ts       # Client configuration
│   │   ├── core/               # SDK core (auth, params, SSE, serializers)
│   │   ├── client/             # Client module (types, utils)
│   │   └── index.ts            # Barrel exports
│   ├── stores/                 # Zustand stores (2 stores)
│   │   ├── preferences-store.ts  # User preferences (164 lines)
│   │   └── keyword-store.ts    # Keyword search state (82 lines)
│   ├── hooks/                  # Custom hooks
│   │   └── use-sse.ts          # SSE streaming hook (188 lines)
│   ├── auth/                   # Auth context
│   │   └── auth-context.tsx    # Auth provider (196 lines)
│   ├── utils/                  # Utility modules
│   │   ├── parse-citations.ts  # Citation parsing (253 lines)
│   │   ├── verse-url.ts        # Verse URL utilities (131 lines)
│   │   ├── arabic.ts           # Arabic text utilities
│   │   ├── hebrew.ts           # Hebrew text utilities
│   │   └── greek.ts            # Greek text utilities
│   ├── logger.ts               # Structured logger (431 lines)
│   ├── correlation.ts          # Correlation ID management (119 lines)
│   ├── design-system.ts        # Theme tokens
│   ├── utils.ts                # cn() + general utils
│   ├── api-client-setup.ts     # API client initialization
│   └── api-provider.tsx        # API provider component
├── __tests__/                  # Vitest + RTL (35 files)
│   ├── compare-page.test.tsx
│   ├── keyword-search-page.test.tsx
│   ├── keyword-search-components.test.tsx
│   ├── keyword-search-auth.test.tsx
│   ├── search-page.test.tsx
│   ├── auth-ui-provider.test.tsx
│   ├── history.test.tsx
│   ├── home-page.test.tsx
│   ├── homepage.test.tsx
│   ├── settings.test.tsx
│   ├── quran.test.tsx
│   ├── old-testament.test.tsx
│   ├── new-testament.test.tsx
│   ├── apocrypha.test.tsx
│   ├── filter-tabs.test.tsx
│   ├── inline-citation.test.tsx
│   ├── parse-citations.test.tsx
│   ├── source-badge.test.tsx
│   ├── source-reference-card.test.tsx
│   ├── search-tabs.test.tsx
│   ├── offline-banner.test.tsx
│   ├── use-sse.test.tsx
│   ├── root-browser-virtuoso.test.tsx
│   ├── root-detail-page.test.tsx
│   ├── rich-root-card.test.tsx
│   ├── large-name-footer.test.tsx
│   ├── etymology-popup.test.tsx
│   ├── translation-block.test.tsx
│   ├── verse-detail.test.tsx
│   ├── example.test.tsx
│   └── i18n/                   # i18n tests (5 files)
└── messages/                   # i18n (en.json, tr.json)
```

## WHERE TO LOOK

| Task                         | Location                     | Notes                                                    |
| ---------------------------- | ---------------------------- | -------------------------------------------------------- |
| Add page                     | `app/[route]/page.tsx`       | App Router convention                                    |
| Add UI primitive             | `components/ui/`             | Radix + library primitives (26 files)                    |
| Add compare component        | `components/compare/`        | 7 domain components                                      |
| Add keyword search component | `components/keyword-search/` | 12 domain components                                     |
| Add verse lookup component   | `components/verse-lookup/`   | 2 files                                                  |
| Add search component         | `components/search/`         | 4 search-related components                              |
| Modify API client            | `lib/api/`                   | Regenerate, don't edit manually                          |
| Add state                    | `lib/stores/`                | Zustand pattern                                          |
| Add hook                     | `lib/hooks/`                 | Custom React hooks                                       |
| Add test                     | `__tests__/`                 | Vitest + RTL (35 test files, 378+ passing)               |
| i18n strings                 | `messages/`                  | en.json, tr.json                                         |
| Add utility                  | `lib/utils/`                 | Domain-specific utils (verse-url, parse-citations, etc.) |
| Modify logging               | `lib/logger.ts`              | Structured logger (196 lines)                            |
| Modify correlation           | `lib/correlation.ts`         | Correlation ID management (72 lines)                     |
| Modify API setup             | `lib/api-client-setup.ts`    | API interceptors (79 lines)                              |
| Modify auth                  | `lib/auth/auth-context.tsx`  | Auth context provider                                    |

## CONVENTIONS

### State Management (Hybrid)

| Type                 | Tool              | Location                          |
| -------------------- | ----------------- | --------------------------------- |
| User preferences     | Zustand + persist | `lib/stores/preferences-store.ts` |
| Keyword search state | Zustand           | `lib/stores/keyword-store.ts`     |
| Server data          | TanStack Query    | `lib/api/@tanstack/`              |
| Auth session         | React Context     | `lib/auth/auth-context.tsx`       |
| URL state            | nuqs              | Page components                   |

### API Client

```typescript
// DO: Use generated client
import { searchQuran } from '@/lib/api';
const results = await searchQuran({ query: 'sabir' });

// DON'T: Raw fetch (except auth/streaming)
fetch('/api/search/quran', { ... });  // Avoid
```

**Exception**: Auth endpoints and SSE streaming use raw `fetch` (circular dependency avoidance).

**SDK Auth Configuration:**

```typescript
// Global auth configured in lib/api/config.ts — called once in layout.tsx
// All SDK functions auto-inject Authorization header
// No manual token handling needed in components
```

### Streaming (SSE)

```typescript
// Use custom hook for EventSource
import { useSSE } from "@/lib/hooks/use-sse"
const { data, error, isConnected } = useSSE("/api/stream/search?q=...")
```

### Components

- **Functional only** - No class components
- **Props interface** - Explicit types, no `any`
- **cn() utility** - Tailwind class merging from `lib/utils.ts`
- **Framer Motion** - Spring animations for transitions
- **Error boundaries** - `error-boundary.tsx` + `global-error.tsx`

### Logging

```typescript
// DO: Use structured logger
import { logger } from "@/lib/logger"
logger.info("Search completed", { query, resultCount })

// DON'T: Use console.log
console.log("Search completed") // Forbidden
```

### Correlation IDs

```typescript
// Correlation IDs managed in lib/correlation.ts
// Auto-injected into API requests for request tracing
```

## GOLDEN RULES

- **Ready component Priority**: ALWAYS prefer ready-made components from established libraries (shadcn/ui, Magic UI, Motion Primitives, Luxe, Kokonut UI, etc.) over manual component creation. Manual components should ONLY be created when no suitable ready-made alternative exists.

### Approved Component Libraries (priority order)

| Layer        | Library            | Use Case                                                     |
| ------------ | ------------------ | ------------------------------------------------------------ |
| Foundation   | shadcn/ui          | Core UI primitives (already using)                           |
| Motion       | Motion Primitives  | Tasteful animations, text reveals, transitions               |
| Effects      | Magic UI           | Hero effects, particles, backgrounds, NumberTicker           |
| Primitives   | Luxe               | Tailwind v4 + Radix native (magnetic button, shine variants) |
| Functional   | Kokonut UI         | AI chat interfaces, functional UI components                 |
| Supplemental | Eldora UI, Animata | Page blocks, micro-interactions                              |

## ANTI-PATTERNS

- **No `any`** - Types generated from OpenAPI spec
- **No manual API edits** - Regenerate via `npx @hey-api/openapi-ts`
- **No Context for server data** - Use TanStack Query
- **No inline styles** - Use Tailwind classes
- **No console.log** - Use structured logger from `lib/logger.ts`
- **No manual components when a library alternative exists** - Search approved libraries first

## KEY COMPONENTS

### Compare Domain (`components/compare/`)

| Component                   | Lines | Role                                       |
| --------------------------- | ----- | ------------------------------------------ |
| `analysis-progress.tsx`     | 209   | Multi-agent analysis progress indicator    |
| `collection-selector.tsx`   | 109   | Collection selection for comparison        |
| `source-reference-card.tsx` | 105   | Verse card with source badge               |
| `citation-hover-card.tsx`   | 98    | Citation tooltip on hover                  |
| `inline-citation.tsx`       | 53    | Clickable inline citation                  |
| `filter-tabs.tsx`           | 40    | Source filtering tabs (AnimatedBackground) |
| `source-badge.tsx`          | 35    | Colored source badge                       |

### Keyword Search Domain (`components/keyword-search/`)

| Component                     | Lines | Role                                         |
| ----------------------------- | ----- | -------------------------------------------- |
| `root-browser.tsx`            | 234   | Root morphology browser                      |
| `verse-card.tsx`              | 181   | Verse display card                           |
| `surah-chart.tsx`             | 169   | Surah/book distribution chart                |
| `accuracy-disclaimer.tsx`     | 164   | Accuracy disclaimer modal                    |
| `search-input.tsx`            | 91    | Search input with transliteration            |
| `derived-words.tsx`           | 77    | Derived words display                        |
| `root-card.tsx`               | 54    | Root information card                        |
| `pagination.tsx`              | 54    | Pagination controls                          |
| `stats-bar.tsx`               | 47    | Search statistics bar                        |
| `bible-category-tabs.tsx`     | 40    | Bible category tabs (AnimatedBackground)     |
| `experimental-disclaimer.tsx` | 28    | Experimental feature disclaimer              |
| `language-tabs.tsx`           | 26    | Language selection tabs (AnimatedBackground) |

## TESTING

```bash
npm test                    # Run Vitest
npm test -- --watch         # Watch mode
```

**Pattern**: Integration-style, renders full pages, mocks fetch/hooks.

```typescript
// Example test structure
vi.mock('next/navigation', () => ({ useRouter: () => mockRouter }));
vi.mock('@/lib/auth/auth-context', () => ({ useAuth: () => mockAuth }));

render(<SearchPage />);
await userEvent.type(screen.getByRole('textbox'), 'sabir');
expect(screen.getByText('Results')).toBeInTheDocument();
```

**Coverage**: 35 test files, 378+ passing tests covering pages, components, hooks, utilities, and i18n.

## COMMANDS

```bash
npm run dev                 # Dev server :3000
npm run build               # Production build
npm test                    # Vitest tests
npx @hey-api/openapi-ts     # Regenerate API client
```

## ARABIC FONT

Arabic text uses **Amiri** font from Google Fonts (classic Naskh calligraphy style).

### Configuration

**layout.tsx:**

```typescript
import { Inter, Amiri } from "next/font/google"

const amiri = Amiri({
  subsets: ["arabic"],
  weight: ["400", "700"],
  variable: "--font-arabic",
  display: "swap",
})
```

**globals.css:**

```css
.font-arabic {
  font-family: var(--font-arabic), "Amiri", serif;
  line-height: 2; /* Extra space for diacritics */
  direction: rtl; /* Right-to-left */
  text-align: right;
}
```

### Usage

```tsx
<p lang="ar" className="font-arabic text-2xl">
  بِسۡمِ ٱللَّهِ ٱلرَّحۡمَٰنِ ٱلرَّحِيمِ
</p>
```

### Changing Font

To switch Arabic font, update only `layout.tsx`:

1. Change import: `Amiri` → `Scheherazade_New`, `Noto_Naskh_Arabic`, etc.
2. Update const name and reference in body className

Available Google Fonts for Arabic:

- `Amiri` - Classic calligraphy (current)
- `Scheherazade_New` - Traditional Naskh
- `Noto_Naskh_Arabic` - Clean, modern
- `Cairo` - Sans-serif
- `Tajawal` - Modern sans-serif

## PERFORMANCE PATTERNS

### React Key Stability (Issue #94)

**Problem**: Index-based keys (`key={i}`) cause reconciliation bugs when lists reorder.

**Solution Patterns**:

- **Domain ID keys**: `key={result.reference}` for unique data
- **Composite keys**: `key={`${citation.reference}-${idx}`}` for duplicate values
- **Namespaced skeleton keys**: `key="root-browser-skeleton-${i}"` for deterministic placeholders

**Files Updated**: 53 files across search, compare, keyword-search, and shared UI components

### SSE Single-Pass Aggregation (Issue #92, #104)

**Problem**: Multiple `.filter().map().find()` passes over SSE data on every message.

**Solution**: Single `.reduce()` pass + ref-based tracking:

```typescript
const sseProcessedCount = useRef(0)
const newMessages = sseData.slice(sseProcessedCount.current)
const streamState = newMessages.reduce((acc, msg) => {
  // Aggregate tokens, verse_details, errors in one pass
}, initialState)
```

**Benefit**: 4x reduction in array iterations

### Zustand Selector-Based Subscriptions (Issue #90)

**Problem**: Full store subscription causes re-renders when any field changes.

**Solution**: Narrow selectors:

```typescript
// ✅ Subscribe only to used fields
const advancedMode = useKeywordStore((s) => s.advancedMode)
const keywords = useKeywordStore((s) => s.keywords)
```

**Benefit**: Re-renders only when subscribed fields change

### React-Virtuoso Virtualization (Issue #91, #156)

**Problem**: Rendering 1,600+ roots causes layout thrashing.

**Solution**: `react-virtuoso` `Virtuoso` component renders only visible rows (~10 instead of 1,600)

### Batched DOM Reads (Issue #91)

**Pattern**: Use `useLayoutEffect` to batch geometry reads before paint

- Tab indicator reads both active and hover geometry in one pass
- Equality checks prevent state updates if geometry unchanged

### Cached Bounds (Issue #91)

**Pattern**: Cache `getBoundingClientRect()` on `mouseenter`, reuse during `mousemove`

- Reduces DOM reads from ~60/sec to 1

### Bundle Optimization (Issue #85)

- **DevTools lazy-load**: `next/dynamic` with `ssr: false` (100-200KB savings)
- **Direct date-fns imports**: Subpath imports for guaranteed tree-shaking (~40KB savings)
- **Recharts code-split**: `next/dynamic` lazy-load (~50KB savings)

## NOTES

- **API client**: Generated from `http://localhost:8000/openapi.json`
- **Design system**: `lib/design-system.ts` defines theme tokens
- **MagicCard**: Magic UI animated card component used throughout (replaced manual GlowCard)
- **Component libraries**: Magic UI (MagicCard, ShimmerButton, BentoGrid, DotPattern), Motion Primitives (AnimatedBackground)
- **Script utilities**: Arabic, Hebrew, Greek text utils in `lib/utils/`
- **Correlation IDs**: Request tracing via `lib/correlation.ts`
- **Structured logging**: Use `logger.child()` not `console.log` (196 lines in `lib/logger.ts`)
- **Test coverage**: 35 test files, 378+ passing tests
