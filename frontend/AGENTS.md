# FRONTEND - KNOWLEDGE BASE

## OVERVIEW

Next.js 15 App Router with Framer Motion animations, Zustand state, and TanStack Query. Generated TypeScript API client from OpenAPI spec. Linear-style dark theme.

## STRUCTURE

```
frontend/
├── app/                        # App Router pages
│   ├── layout.tsx              # Root layout + providers
│   ├── page.tsx                # Landing page
│   ├── login/                  # Auth pages
│   ├── register/
│   ├── search/                 # Quran search
│   ├── compare/                # Multi-agent comparison (462 lines)
│   ├── history/                # Search history
│   ├── settings/               # User preferences
│   └── [scripture]/            # OT, NT, Apocrypha, Quran browse
├── components/
│   ├── ui/                     # Radix primitives (11 files)
│   ├── layout/                 # Navigation, headers
│   ├── search/                 # Domain components
│   └── providers.tsx           # Root provider composition
├── lib/
│   ├── api/                    # Generated client (1003+ lines)
│   │   ├── types.gen.ts        # TypeScript types from OpenAPI
│   │   ├── sdk.gen.ts          # API methods
│   │   └── @tanstack/          # React Query hooks
│   ├── stores/                 # Zustand stores
│   ├── hooks/                  # Custom hooks (SSE, etc.)
│   └── auth/                   # Auth context
├── __tests__/                  # Vitest + RTL (8 files)
└── messages/                   # i18n (en.json, tr.json)
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add page | `app/[route]/page.tsx` | App Router convention |
| Add UI component | `components/ui/` | Radix + Tailwind |
| Add domain component | `components/[domain]/` | Feature-specific |
| Modify API client | `lib/api/` | Regenerate, don't edit manually |
| Add state | `lib/stores/` | Zustand pattern |
| Add hook | `lib/hooks/` | Custom React hooks |
| Add test | `__tests__/` | Vitest + RTL |
| i18n strings | `messages/` | en.json, tr.json |

## CONVENTIONS

### State Management (Hybrid)

| Type | Tool | Location |
|------|------|----------|
| User preferences | Zustand + persist | `lib/stores/preferences-store.ts` |
| Server data | TanStack Query | `lib/api/@tanstack/` |
| Auth session | React Context | `lib/auth/auth-context.tsx` |
| URL state | nuqs | Page components |

### API Client

```typescript
// DO: Use generated client
import { searchQuran } from '@/lib/api';
const results = await searchQuran({ query: 'sabir' });

// DON'T: Raw fetch (except auth/streaming)
fetch('/api/search/quran', { ... });  // Avoid
```

**Exception**: Auth endpoints and SSE streaming use raw `fetch` (circular dependency avoidance).

### Streaming (SSE)

```typescript
// Use custom hook for EventSource
import { useSSE } from '@/lib/hooks/use-sse';
const { data, error, isConnected } = useSSE('/api/stream/search?q=...');
```

### Components

- **Functional only** - No class components
- **Props interface** - Explicit types, no `any`
- **cn() utility** - Tailwind class merging from `lib/utils.ts`
- **Framer Motion** - Spring animations for transitions

## ANTI-PATTERNS

- **No `any`** - Types generated from OpenAPI spec
- **No manual API edits** - Regenerate via `npx @hey-api/openapi-ts`
- **No Context for server data** - Use TanStack Query
- **No inline styles** - Use Tailwind classes
- **No console.log** - Use proper error boundaries

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
import { Inter, Amiri } from "next/font/google";

const amiri = Amiri({
  subsets: ["arabic"],
  weight: ["400", "700"],
  variable: "--font-arabic",
  display: "swap",
});
```

**globals.css:**
```css
.font-arabic {
  font-family: var(--font-arabic), 'Amiri', serif;
  line-height: 2;        /* Extra space for diacritics */
  direction: rtl;        /* Right-to-left */
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

## NOTES

- **Zombie status**: Documentation claims "frontend removed" but code exists. Verify intent before major changes.
- **API client**: Generated from `http://localhost:8000/openapi.json`
- **Design system**: `lib/design-system.ts` defines theme tokens
- **GlowCard**: Custom animated card component used throughout
