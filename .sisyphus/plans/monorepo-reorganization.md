# Monorepo Reorganization & Frontend MVP

## Context

### Original Request
Kullanici, Sacred Texts RAG projesine frontend eklemek istiyor. Bunun icin once backend kodlarini `backend/` klasorune, frontend kodlarini `frontend/` klasorune organize etmek gerekiyor.

### Interview Summary

**Key Discussions**:
- **Kapsam**: MVP (Landing Page + Auth + Unified Search)
- **Tema**: Dark Mode Only (Linear/Raycast estetigi)
- **Arapca**: Goruntuleme + Tecvid (statik veri)
- **Auth**: Zorunlu (Email/Sifre + Google OAuth)
- **Hedef Kitle**: Genel kullanicilar
- **Streaming**: LLM cevaplari icin SSE
- **Arama**: Birlesik (Quran + Bible tek sorguda)
- **Landing**: Minimal Hero
- **i18n**: TR/EN

**Research Findings**:
- Backend 92 import statement kullaniyor (`from src.`, `from app.`)
- Dosyalar `backend/` klasorune tasinmis (TODO reorg-1 to reorg-4)
- Import'lar PYTHONPATH ile calisacak (kod degisikligi gerekmez)
- FastAPI OpenAPI schema `/docs` adresinde mevcut

### Metis Review

**Identified Gaps** (addressed):
1. `.env` dosyasi konumu belirsizdi → Root'ta kalacak, symlink olusturulacak
2. Working directory belirsizdi → `backend/` icinden calistirilacak
3. Token expire edge case → Reconnect with refresh token
4. Empty search handling → Button disabled + validation error

---

## Work Objectives

### Core Objective
Projeyi monorepo yapisina donustur ve "Utilitarian Luxury" (Linear/Raycast) standartlarinda frontend MVP olustur.

### Concrete Deliverables
- `backend/` klasorunde calisan Python backend
- `frontend/` klasorunde Next.js 15 MVP uygulamasi (endustri standardi)
- Guncelenmis docker-compose.yml ve scripts

### Definition of Done
- [ ] `cd backend && python main.py search "sabir"` → Sonuc doner
- [ ] `cd backend && uvicorn app.main:app --reload` → Hatasiz baslar
- [ ] `cd frontend && npm run dev` → localhost:3000'de acilir
- [ ] Kullanici login/register yapabilir
- [ ] Arama yapildiginda SSE streaming calisir
- [ ] Animasyonlar fiziksel (spring) hissettiriyor
- [ ] UI "Linear" kalitesinde gorunuyor

### Must Have
- Backend import'lari calismali (PYTHONPATH ile)
- Frontend API client OpenAPI'den uretilmeli
- Dark mode tema (Linear Zinc palette)
- TR/EN i18n
- Google OAuth
- **Framer Motion spring animasyonlari**
- **shadcn/ui + Radix UI componentleri**
- **cmdk Command Palette**
- **Optimistic UI pattern**
- **Skeleton loading states**

### Must NOT Have (Guardrails)
- Light mode tema (sadece dark)
- Admin panel
- Favorites/Bookmarks
- Search history page
- Chat history
- Custom API wrappers (sadece @hey-api/openapi-ts)
- Manual fetch calls
- Analytics/tracking
- E2E tests (Phase 3)
- User documentation
- CSS transition/ease (sadece spring physics)
- MUI, Ant Design veya diger UI kit'ler

---

## Design System Specification (Linear Standard)

### Color Palette (CSS Variables)

```css
:root {
  /* Backgrounds - Layered depth */
  --bg-app: #09090b;        /* Zinc-950 - Ana arka plan */
  --bg-surface: #18181b;    /* Zinc-900 - Kartlar, paneller */
  --bg-elevated: #27272a;   /* Zinc-800 - Hover, aktif */
  
  /* Borders - Subtle glow */
  --border-subtle: #27272a; /* Zinc-800 - Pasif sinirlar */
  --border-glow: #3f3f46;   /* Zinc-700 - Aktif, focus */
  
  /* Text hierarchy */
  --text-primary: #f4f4f5;  /* Zinc-100 - Basliklar */
  --text-secondary: #a1a1aa; /* Zinc-400 - Metadata */
  --text-muted: #71717a;    /* Zinc-500 - Placeholder */
  
  /* Accent */
  --accent-primary: #6366f1; /* Indigo-500 - CTA, links */
  --accent-glow: rgba(99, 102, 241, 0.15); /* Glow effect */
}
```

### Typography Scale

| Token | Size | Line Height | Letter Spacing | Usage |
|-------|------|-------------|----------------|-------|
| `text-xs` | 12px | 16px | 0.02em | Badges, timestamps |
| `text-sm` | 13px | 18px | 0.01em | Secondary labels, dense lists |
| `text-base` | 14px | 20px | 0 | Body text, inputs |
| `text-md` | 16px | 24px | -0.01em | Modal titles |
| `text-lg` | 18px | 28px | -0.02em | Section headers |
| `text-xl` | 24px | 32px | -0.02em | Page titles |

**Font Stack:**
```css
font-family: 'Inter var', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
font-feature-settings: 'cv05', 'cv08', 'ss01'; /* OpenType features for readability */
```

### Spring Animation Presets

| Interaction Type | Stiffness | Damping | Mass | Usage |
|------------------|-----------|---------|------|-------|
| **Snappy** | 300-400 | 30-35 | 1 | Dropdowns, tooltips, toggles |
| **Fluid** | 170-200 | 20-26 | 1 | Page transitions, modals |
| **Gentle** | 100-120 | 14-20 | 1 | Large content blocks, skeletons |

**Framer Motion Config:**
```typescript
export const springPresets = {
  snappy: { type: "spring", stiffness: 300, damping: 30 },
  fluid: { type: "spring", stiffness: 170, damping: 26 },
  gentle: { type: "spring", stiffness: 120, damping: 14 },
};
```

### Component Standards

**Buttons:**
- Height: 32px (sm), 36px (md), 40px (lg)
- Border radius: 6px
- Focus ring: 2px offset, accent color
- Hover: Scale 1.02, bg-elevated

**Inputs:**
- Height: 36px (default), 40px (large)
- Border: 1px --border-subtle
- Focus: --border-glow + box-shadow glow
- Placeholder: --text-muted

**Cards:**
- Background: --bg-surface
- Border: 1px --border-subtle
- Hover: border --border-glow
- Border radius: 8px

---

## Verification Strategy (MANDATORY)

### Test Decision
- **Infrastructure exists**: YES (backend tests mevcut)
- **User wants tests**: Manual verification for MVP
- **Framework**: pytest (backend), manual (frontend)

### Manual QA for Frontend
Her task icin detayli verification procedure belirlendi.

---

## Task Flow

```
PHASE 1: Backend Reorganization
  1.1 → 1.2 → 1.3 → 1.4 (sequential)

PHASE 2: Frontend Foundation
  2.1 → 2.2 → 2.3 → 2.4 (sequential)

PHASE 3: Frontend Features
  3.1 (Auth) → 3.2 (Landing) → 3.3 (Search)

PHASE 4: Polish
  4.1 (i18n) → 4.2 (Final Test)
```

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| A | 3.2, 3.3 | After 3.1, parallel possible |

---

## TODOs

### PHASE 1: Backend Reorganization

- [ ] 1.1. Fix dev.sh script paths

  **What to do**:
  - Update `backend/scripts/dev.sh` to:
    - Navigate to project root for docker-compose
    - Set PYTHONPATH=. when running uvicorn
    - cd to backend/ before running uvicorn
  - Update uvicorn command: `cd backend && PYTHONPATH=. uvicorn app.main:app --reload`

  **Must NOT do**:
  - Change Python import statements
  - Modify docker-compose.yml location

  **Parallelizable**: NO (first task)

  **References**:
  - `backend/scripts/dev.sh` - Current script needing fixes
  - `docker-compose.yml` (root) - Container definitions

  **Acceptance Criteria**:
  - [ ] `./backend/scripts/dev.sh` starts all services
  - [ ] PostgreSQL container starts (port 54322)
  - [ ] Qdrant container starts (port 6333)
  - [ ] FastAPI starts without import errors

  **Commit**: YES
  - Message: `fix(backend): update dev.sh for monorepo structure`
  - Files: `backend/scripts/dev.sh`

---

- [ ] 1.2. Create .env symlink for backend

  **What to do**:
  - Create symlink: `ln -s ../.env backend/.env`
  - OR update `backend/app/config.py` to use `env_file = "../.env"`
  - Verify environment variables load correctly

  **Must NOT do**:
  - Duplicate .env file
  - Move original .env

  **Parallelizable**: NO (depends on 1.1)

  **References**:
  - `.env` (root) - Environment variables
  - `backend/app/config.py:Settings` - Pydantic settings class

  **Acceptance Criteria**:
  - [ ] `cd backend && python -c "from app.config import settings; print(settings.openrouter_api_key[:10])"` → API key prefix
  - [ ] No "env file not found" warnings

  **Commit**: YES
  - Message: `fix(backend): add .env symlink for monorepo`
  - Files: `backend/.env` (symlink) OR `backend/app/config.py`

---

- [ ] 1.3. Test backend CLI commands

  **What to do**:
  - Run from backend directory with PYTHONPATH
  - Test: `PYTHONPATH=. python main.py info`
  - Test: `PYTHONPATH=. python main.py search "sabir"`
  - Test: `PYTHONPATH=. python main.py ask "Islam'da sabir nedir?"`
  - Fix any path issues found

  **Must NOT do**:
  - Change business logic
  - Modify RAG pipeline

  **Parallelizable**: NO (depends on 1.2)

  **References**:
  - `backend/main.py` - CLI entrypoint
  - `backend/src/ultimate_rag.py` - RAG pipeline

  **Acceptance Criteria**:
  - [ ] `cd backend && PYTHONPATH=. python main.py info` → Shows collection info
  - [ ] `cd backend && PYTHONPATH=. python main.py search "sabir"` → Returns verses
  - [ ] `cd backend && PYTHONPATH=. python main.py ask "test"` → Returns answer

  **Commit**: NO (verification only)

---

- [ ] 1.4. Test backend API endpoints

  **What to do**:
  - Start API: `cd backend && PYTHONPATH=. uvicorn app.main:app --reload`
  - Test health: `curl http://localhost:8000/api/health`
  - Test docs: Open `http://localhost:8000/docs`
  - Test auth: `curl -X POST http://localhost:8000/api/auth/register -H "Content-Type: application/json" -d '{"email":"test@test.com","password":"test123"}'`

  **Must NOT do**:
  - Change API response formats
  - Modify authentication flow

  **Parallelizable**: NO (depends on 1.3)

  **References**:
  - `backend/app/main.py` - FastAPI app
  - `backend/app/api/` - Route handlers

  **Acceptance Criteria**:
  - [ ] `curl http://localhost:8000/api/health` → `{"status": "healthy"}`
  - [ ] `http://localhost:8000/docs` → OpenAPI UI loads
  - [ ] Register endpoint returns JWT tokens

  **Commit**: YES (if any fixes made)
  - Message: `fix(backend): ensure API works in monorepo structure`
  - Files: Any modified files

---

### PHASE 2: Frontend Foundation (Linear Standard)

- [ ] 2.1. Initialize Next.js 15 project with full stack

  **What to do**:
  - Create Next.js 15 project:
    ```bash
    npx create-next-app@latest frontend \
      --typescript \
      --tailwind \
      --app \
      --no-src-dir \
      --import-alias "@/*"
    ```
  - Install ALL required dependencies:
    ```bash
    cd frontend
    
    # State & Data
    npm install @tanstack/react-query @tanstack/react-query-devtools
    
    # Animation (CRITICAL - Spring physics)
    npm install framer-motion
    
    # UI Components
    npm install lucide-react sonner
    npm install cmdk  # Command palette
    
    # Forms & Validation
    npm install nuqs zod react-hook-form @hookform/resolvers
    
    # i18n
    npm install next-intl
    
    # API Client Generation
    npm install -D @hey-api/openapi-ts
    ```
  - Initialize shadcn/ui:
    ```bash
    npx shadcn@latest init
    # Style: New York (daha kompakt)
    # Base color: Zinc
    # CSS variables: Yes
    ```
  - Add essential shadcn components:
    ```bash
    npx shadcn@latest add button input card dialog
    npx shadcn@latest add dropdown-menu popover tooltip
    npx shadcn@latest add skeleton separator
    ```

  **Must NOT do**:
  - Use Pages Router (App Router only)
  - Install MUI, Ant Design, Chakra
  - Skip any dependency (hepsi gerekli)
  - Use default shadcn colors (Zinc olmali)

  **Parallelizable**: NO (after Phase 1)

  **References**:
  - `Frontend-info/Frontend Teknoloji Yigini Secimi.md` - Tech stack
  - `Frontend-info/_Kurumsal Tasarim Sistemleri.md` - Design system

  **Acceptance Criteria**:
  - [ ] `cd frontend && npm run dev` → localhost:3000
  - [ ] `framer-motion` installed (check package.json)
  - [ ] `cmdk` installed (check package.json)
  - [ ] `frontend/components/ui/button.tsx` exists (shadcn)
  - [ ] `frontend/components/ui/skeleton.tsx` exists
  - [ ] Tailwind config has Zinc as base

  **Commit**: YES
  - Message: `feat(frontend): initialize Next.js 15 with shadcn/ui and animation stack`
  - Files: `frontend/` (new folder)

---

- [ ] 2.2. Setup Design System (Linear Standard)

  **What to do**:
  - Create `frontend/lib/design-system.ts` with:
    - Spring animation presets (snappy, fluid, gentle)
    - Color tokens as constants
    - Typography scale
  - Update `frontend/app/globals.css`:
    - Add CSS variables from Design System Specification above
    - Set dark mode as default (no light mode)
    - Add Inter font with OpenType features
  - Update `frontend/tailwind.config.ts`:
    - Extend colors with CSS variables
    - Add custom animations using spring presets
    - Configure font family
  - Create `frontend/components/motion.tsx`:
    - Export pre-configured motion components
    - `MotionDiv`, `MotionButton` with default spring
    - `AnimatePresence` wrapper

  **Must NOT do**:
  - Add light mode support
  - Use CSS ease/transition (only spring)
  - Deviate from Zinc palette

  **Parallelizable**: NO (depends on 2.1)

  **References**:
  - `Frontend-info/_Kurumsal Tasarim Sistemleri.md:2.1.1` - Spring parameters
  - `Frontend-info/Web Uygulamasi UI_UX.md:2.1` - Color palette
  - Design System Specification section above

  **Acceptance Criteria**:
  - [ ] `globals.css` has all CSS variables defined
  - [ ] Body background is `--bg-app` (#09090b)
  - [ ] Inter font loads with OpenType features
  - [ ] `springPresets.snappy` exportable from design-system.ts
  - [ ] No `transition` or `ease` in CSS (only spring)

  **Commit**: YES
  - Message: `feat(frontend): setup Linear-style design system with spring animations`
  - Files: `globals.css`, `tailwind.config.ts`, `lib/design-system.ts`, `components/motion.tsx`

---

- [ ] 2.3. Generate API client from OpenAPI

  **What to do**:
  - Ensure backend is running on port 8000
  - Generate type-safe API client:
    ```bash
    cd frontend
    npx @hey-api/openapi-ts \
      -i http://localhost:8000/openapi.json \
      -o lib/api \
      -c @tanstack/react-query
    ```
  - Create `frontend/lib/api-provider.tsx`:
    - Setup QueryClient with optimistic update defaults
    - Configure stale time, retry logic
    - Export provider component

  **Must NOT do**:
  - Write manual fetch functions
  - Create custom axios wrappers
  - Modify generated types

  **Parallelizable**: NO (depends on 2.2, needs running backend)

  **References**:
  - `http://localhost:8000/openapi.json` - API schema
  - `Frontend-info/Frontend Teknoloji Yigini Secimi.md:4.1` - Schema-first

  **Acceptance Criteria**:
  - [ ] `frontend/lib/api/` contains generated types
  - [ ] TypeScript types match backend Pydantic models
  - [ ] `useQuery` and `useMutation` hooks generated
  - [ ] No manual fetch/axios code

  **Commit**: YES
  - Message: `feat(frontend): generate type-safe API client from OpenAPI`
  - Files: `frontend/lib/api/`, `frontend/lib/api-provider.tsx`

---

- [ ] 2.4. Create base layout with providers

  **What to do**:
  - Update `frontend/app/layout.tsx`:
    - Wrap with QueryClientProvider
    - Add Sonner Toaster (dark theme)
    - Set metadata (title, description)
    - Apply Inter font class
  - Create `frontend/components/providers.tsx`:
    - Combine all providers (Query, Theme, etc.)
  - Create `frontend/components/ui/glow-card.tsx`:
    - Card with Linear-style border glow on hover
    - Use Framer Motion for hover animation
  - Create `frontend/components/ui/magnetic-button.tsx`:
    - Button that moves toward cursor on hover
    - Spring animation for magnetic effect

  **Must NOT do**:
  - Add theme toggle (dark only)
  - Create complex navigation yet

  **Parallelizable**: NO (depends on 2.3)

  **References**:
  - `Frontend-info/Web Uygulamasi UI_UX.md:3.1` - Magnetic buttons
  - `Frontend-info/_Kurumsal Tasarim Sistemleri.md:2.3` - Glow effects

  **Acceptance Criteria**:
  - [ ] Page renders with dark background (#09090b)
  - [ ] Sonner toasts appear in bottom-right
  - [ ] GlowCard border glows on hover (spring animation)
  - [ ] MagneticButton moves toward cursor
  - [ ] No flash of unstyled content

  **Commit**: YES
  - Message: `feat(frontend): create base layout with spring-animated components`
  - Files: `layout.tsx`, `providers.tsx`, `glow-card.tsx`, `magnetic-button.tsx`

---

### PHASE 3: Frontend Features

- [ ] 3.1. Implement authentication pages

  **What to do**:
  - Create `/login/page.tsx`:
    - Glassmorphism card (backdrop-blur)
    - Email/password inputs with glow focus
    - Google OAuth button (magnetic effect)
    - Spring animated form appearance
    - Skeleton loading during auth check
  - Create `/register/page.tsx`:
    - Same design as login
    - Zod validation with react-hook-form
  - Create `frontend/lib/auth/`:
    - Auth context with token management
    - Protected route wrapper
    - Optimistic login (UI updates before server confirms)
  - Implement logout with spring exit animation

  **Must NOT do**:
  - Store tokens in localStorage (httpOnly cookies)
  - Add forgot password
  - Add email verification
  - Use CSS transitions (spring only)

  **Parallelizable**: NO (depends on 2.4)

  **References**:
  - `backend/app/api/auth.py` - Auth endpoints
  - `Frontend-info/Web Uygulamasi UI_UX.md:5.1` - Auth design
  - `Frontend-info/_Kurumsal Tasarim Sistemleri.md:2.2` - Glassmorphism

  **Acceptance Criteria**:
  - [ ] Login form has glassmorphism background
  - [ ] Input focus shows glow effect (spring)
  - [ ] Form appears with fluid spring animation
  - [ ] Google button has magnetic hover effect
  - [ ] Loading state shows skeleton
  - [ ] Successful login shows optimistic redirect
  - [ ] Playwright test:
    - Navigate to /login
    - Fill credentials
    - Submit → verify redirect animation

  **Commit**: YES
  - Message: `feat(frontend): implement auth pages with spring animations`
  - Files: `app/login/`, `app/register/`, `lib/auth/`

---

- [ ] 3.2. Create landing page (Minimal Hero)

  **What to do**:
  - Create `/page.tsx` with:
    - Full-screen dark gradient background
    - Large centered search input (glow on focus)
    - Animated tagline: "Kutsal Metinlerde Arama"
    - CTA buttons with magnetic effect
    - Subtle particle/grain background (optional)
  - Implement Linear-style text gradient on title
  - Add staggered entrance animations (spring)
  - Search input redirects to /login if not authenticated

  **Must NOT do**:
  - Add Bento grid (MVP'de yok)
  - Create complex animations
  - Allow search without auth

  **Parallelizable**: YES (with 3.3 after 3.1)

  **References**:
  - `Frontend-info/Web Uygulamasi UI_UX.md:4.1` - Hero design
  - `Frontend-info/_Kurumsal Tasarim Sistemleri.md:2.3` - Glow effects
  - Linear.app landing page - Visual reference

  **Acceptance Criteria**:
  - [ ] Hero loads with staggered spring animation
  - [ ] Title has metallic gradient effect
  - [ ] Search input glows on focus
  - [ ] Buttons have magnetic hover
  - [ ] Clicking search → redirects to /login
  - [ ] Background has subtle depth

  **Commit**: YES
  - Message: `feat(frontend): create Linear-style hero landing page`
  - Files: `app/page.tsx`

---

- [ ] 3.3. Implement unified search with SSE streaming

  **What to do**:
  - Create `/search/page.tsx` (protected route):
    - Command palette style input (cmdk)
    - Real-time streaming results
    - Spring animated result cards
  - Create `frontend/components/search/`:
    - `SearchInput.tsx` - cmdk style with glow
    - `SearchResults.tsx` - Animated list with layout animations
    - `VerseCard.tsx` - Result card with hover glow
    - `StreamingText.tsx` - Typewriter effect for LLM response
  - Implement SSE connection:
    - Connect to `/api/stream/search`
    - Handle token-by-token streaming
    - Optimistic UI during search
  - Arabic text support:
    - RTL direction for Quran verses
    - Amiri font for Arabic
  - Rate limit display:
    - "X/50 arama kaldi" indicator
    - Warning when low (< 10)
  - Error handling:
    - Sonner toast for errors
    - Retry button with spring animation

  **Must NOT do**:
  - Add filters or facets
  - Implement search history UI
  - Add bookmarking
  - Use CSS transitions (spring for everything)

  **Parallelizable**: YES (with 3.2 after 3.1)

  **References**:
  - `backend/app/api/stream.py` - SSE endpoint format
  - `Frontend-info/Web Uygulamasi UI_UX.md:6.4` - Perplexity-style
  - `Frontend-info/_Kurumsal Tasarim Sistemleri.md:4.1` - cmdk

  **Acceptance Criteria**:
  - [ ] Search input has cmdk styling
  - [ ] Results animate in with staggered spring
  - [ ] SSE tokens stream smoothly
  - [ ] Arabic text is RTL with Amiri font
  - [ ] Rate limit shows remaining count
  - [ ] Error shows toast notification
  - [ ] VerseCard has hover glow effect
  - [ ] Layout animation when results change
  - [ ] Playwright test:
    - Login → Navigate to /search
    - Type query → Submit
    - Verify streaming text appears
    - Verify spring animations visible

  **Commit**: YES
  - Message: `feat(frontend): implement unified search with SSE and spring animations`
  - Files: `app/search/`, `components/search/`

---

### PHASE 4: Polish

- [ ] 4.1. Add i18n support (TR/EN)

  **What to do**:
  - Configure next-intl:
    - Create `frontend/i18n.ts` configuration
    - Setup middleware for locale detection
  - Create message files:
    - `frontend/messages/tr.json` - Turkce UI
    - `frontend/messages/en.json` - English UI
  - Add language switcher:
    - Dropdown in header/footer
    - Animated with spring on open
    - Persist selection in cookie
  - Translate all UI strings:
    - Auth pages
    - Landing page
    - Search page
    - Error messages
    - Placeholders

  **Must NOT do**:
  - Add more languages (only TR/EN)
  - Translate content (only UI)
  - Use CSS transition for dropdown

  **Parallelizable**: NO (depends on 3.3)

  **References**:
  - next-intl documentation
  - Existing UI text in components

  **Acceptance Criteria**:
  - [ ] Language switcher in UI (animated)
  - [ ] TR → EN changes all text
  - [ ] EN → TR changes all text
  - [ ] Selection persists on refresh
  - [ ] No hardcoded strings remain

  **Commit**: YES
  - Message: `feat(frontend): add TR/EN internationalization`
  - Files: `messages/`, `middleware.ts`, `i18n.ts`

---

- [ ] 4.2. Final integration test and polish

  **What to do**:
  - Run complete user flow:
    1. Open landing page (verify animations)
    2. Click "Kayit Ol" (verify magnetic button)
    3. Register (verify form animations)
    4. Redirect to search (verify transition)
    5. Perform search (verify SSE streaming)
    6. View results (verify spring cards)
    7. Switch language (verify dropdown animation)
    8. Logout (verify exit animation)
    9. Login again (verify flow)
  - Fix any animation/timing issues
  - Verify no CSS transitions (only springs)
  - Performance check:
    - No layout shift (CLS < 0.1)
    - Smooth 60fps animations
  - Update memory-bank documentation

  **Must NOT do**:
  - Add new features
  - Change existing behavior
  - Skip animation verification

  **Parallelizable**: NO (final task)

  **References**:
  - All previous tasks
  - `Frontend-info/_Kurumsal Tasarim Sistemleri.md:7` - Performance checklist

  **Acceptance Criteria**:
  - [ ] Complete flow works end-to-end
  - [ ] All animations are spring-based
  - [ ] No console errors
  - [ ] No TypeScript errors
  - [ ] CLS < 0.1 (no layout shift)
  - [ ] 60fps animations
  - [ ] memory-bank/progress.md updated
  - [ ] memory-bank/techContext.md updated

  **Commit**: YES
  - Message: `docs: update memory-bank for frontend MVP completion`
  - Files: `memory-bank/progress.md`, `memory-bank/techContext.md`

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1.1 | `fix(backend): update dev.sh for monorepo structure` | dev.sh | Services start |
| 1.2 | `fix(backend): add .env symlink for monorepo` | .env or config.py | Config loads |
| 1.4 | `fix(backend): ensure API works in monorepo` | Any fixes | API responds |
| 2.1 | `feat(frontend): initialize Next.js 15 with animation stack` | frontend/ | All deps installed |
| 2.2 | `feat(frontend): setup Linear-style design system` | css, config | Springs work |
| 2.3 | `feat(frontend): generate type-safe API client` | lib/api/ | Types exist |
| 2.4 | `feat(frontend): create base layout with spring components` | layout, components | Magnetic works |
| 3.1 | `feat(frontend): implement auth with spring animations` | login/, register/ | Glassmorphism |
| 3.2 | `feat(frontend): create Linear-style hero landing` | page.tsx | Hero animates |
| 3.3 | `feat(frontend): implement search with SSE and springs` | search/ | SSE + springs |
| 4.1 | `feat(frontend): add TR/EN internationalization` | messages/, i18n | Lang switch |
| 4.2 | `docs: update memory-bank for frontend MVP` | memory-bank/ | Docs updated |

---

## Success Criteria

### Verification Commands

```bash
# Backend
cd backend && PYTHONPATH=. python main.py info
cd backend && PYTHONPATH=. uvicorn app.main:app --reload
curl http://localhost:8000/api/health

# Frontend
cd frontend && npm run dev
# Open http://localhost:3000
```

### Final Checklist

**Functionality:**
- [ ] Backend CLI works from backend/
- [ ] Backend API works from backend/
- [ ] Frontend builds without errors
- [ ] Full user flow works

**Design System (Linear Standard):**
- [ ] Dark mode only (no light mode)
- [ ] Zinc color palette applied
- [ ] Inter font with OpenType features
- [ ] All animations use spring physics
- [ ] No CSS ease/transition anywhere
- [ ] Glassmorphism on auth cards
- [ ] Glow effects on focus/hover
- [ ] Magnetic buttons working
- [ ] Skeleton loading states

**Components:**
- [ ] shadcn/ui components used
- [ ] cmdk command palette style
- [ ] Framer Motion for all animations
- [ ] Sonner for notifications

**Performance:**
- [ ] CLS < 0.1
- [ ] 60fps animations
- [ ] No layout shift

**i18n:**
- [ ] TR/EN working
- [ ] Persists on refresh
