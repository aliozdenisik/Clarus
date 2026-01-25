# Frontend Completion Plan

## Context

### Original Request
Frontend mantık olarak güzel çalışıyor ama çok fazla eksik element, page vs. var - bu eksikleri tamamla.

### Interview Summary
**Key Discussions**:
- Bible Search, Search History, User Preferences, Quran Browse, Bible Browse sayfaları eklenecek
- Global Navigation tüm sayfalarda olacak
- SSE Streaming Search ve Compare için entegre edilecek
- Routing: Ayrı sayfalar (/search, /search-bible, /quran, /bible, /history, /settings)
- Preferences: Dil tercihi + (Profil düzenleme yok - backend desteği yok)
- Mevcut components (GlowCard, Button, Input) kullanılacak
- Zustand global state için eklenecek
- Vitest + RTL test altyapısı kurulacak

**Research Findings**:
- Backend API'leri mevcut: `/api/search/bible`, `/api/preferences`, `/api/metadata/*`, `/api/stream/*`
- Profil düzenleme (isim, şifre değiştirme) backend'de YOK - sadece preferences API var
- lib/api'de SDK henüz generate edilmemiş - manuel fetch kullanılıyor
- SSE client helper yok - oluşturulacak
- Zustand kurulu değil - kurulacak

### Metis Review
**Identified Gaps** (addressed):
- lib/api SDK generate edilmeli (Foundation phase'de)
- Zustand kurulmalı (Foundation phase'de)
- SSE utility hook oluşturulmalı (Foundation phase'de)
- Profil düzenleme backend'de yok - scope'tan çıkarıldı

---

## Work Objectives

### Core Objective
5 yeni sayfa, global navigation, SSE streaming ve test altyapısı ekleyerek frontend'i tamamla.

### Concrete Deliverables
- `frontend/app/search/page.tsx` - Unified search with 4 tabs (Kuran | Eski Ahit | Yeni Ahit | Apokrifa)
- `frontend/app/history/page.tsx` - Search history page
- `frontend/app/settings/page.tsx` - User preferences page
- `frontend/app/quran/page.tsx` - Quran browse page (114 sure listesi)
- `frontend/app/old-testament/page.tsx` - Old Testament browse page (39 kitap)
- `frontend/app/new-testament/page.tsx` - New Testament browse page (27 kitap)
- `frontend/app/apocrypha/page.tsx` - Apocrypha browse page (kitap listesi)
- `frontend/components/layout/navigation.tsx` - Global navigation
- `frontend/components/search/search-tabs.tsx` - 4-tab search component
- `frontend/lib/hooks/use-sse.ts` - SSE streaming hook
- `frontend/lib/stores/preferences-store.ts` - Zustand store
- `vitest.config.ts` + test files for each page

### Definition of Done
- [ ] `npm run dev` → Tüm sayfalar hatasız render
- [ ] `npm test` → Tüm testler geçer
- [ ] `npm run build` → Production build başarılı
- [ ] Navigation tüm sayfalarda görünür
- [ ] SSE streaming Search ve Compare'de çalışır

### Must Have
- 4-tab unified search page (Kuran | Eski Ahit | Yeni Ahit | Apokrifa)
- 4 browse sayfası (Quran, Old Testament, New Testament, Apocrypha)
- History sayfası
- Settings sayfası
- Global Navigation component
- SSE streaming hook
- Zustand preferences store
- Vitest + RTL test altyapısı
- Her yeni sayfa için en az 1 test

### Must NOT Have (Guardrails)
- Profil düzenleme (isim, şifre değiştirme) - backend desteği yok
- Admin Dashboard - scope dışı
- Dark/Light theme toggle - scope dışı
- Arabic/RTL support - scope dışı
- Offline/PWA capabilities
- E2E tests (sadece unit/component tests)
- Bookmarks / Save functionality
- WebSocket real-time chat

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO
- **User wants tests**: YES (Vitest + RTL)
- **Framework**: Vitest + @testing-library/react

### TDD Workflow
Each page follows RED-GREEN-REFACTOR:

1. **RED**: Write failing test first
2. **GREEN**: Implement minimum code to pass
3. **REFACTOR**: Clean up while keeping green

---

## Task Flow

```
Foundation (Sequential):
  1 → 2 → 3 → 4 → 5

Pages (Parallel after Foundation):
  6 ─┬─ 7 ─┬─ 8 ─┬─ 9 ─┬─ 10 ─┬─ 10a ─┬─ 10b
     │     │     │     │      │       │
     └─────┴─────┴─────┴──────┴───────┘

Integration (Sequential):
  11 → 12

Finalization:
  13
```

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| Foundation | 1-5 | Sequential - each depends on previous |
| Pages | 6, 7, 8, 9, 10, 10a, 10b | Parallel - independent pages |
| Integration | 11-12 | Sequential - needs pages complete |

| Task | Depends On | Reason |
|------|------------|--------|
| 2 | 1 | Zustand needs npm install |
| 3 | 2 | SSE hook may use Zustand |
| 4 | 3 | Navigation uses hooks |
| 5 | 4 | Tests need Vitest setup |
| 6-10b | 5 | Pages need foundation complete |
| 11-12 | 6-10b | SSE integration needs pages |
| 13 | 11-12 | Final verification |

---

## TODOs

### FOUNDATION PHASE

- [x] 1. Install Zustand dependency

  **What to do**:
  - Run `npm install zustand` in frontend directory
  - Verify installation in package.json

  **Must NOT do**:
  - Don't create stores yet (next task)

  **Parallelizable**: NO (first task)

  **References**:
  - `frontend/package.json` - Add zustand dependency

  **Acceptance Criteria**:
  - [ ] `npm ls zustand` → shows zustand@x.x.x
  - [ ] `package.json` contains "zustand" in dependencies

  **Commit**: YES
  - Message: `feat(frontend): add zustand for state management`
  - Files: `frontend/package.json`, `frontend/package-lock.json`

---

- [x] 2. Create Zustand preferences store

  **What to do**:
  - Create `frontend/lib/stores/preferences-store.ts`
  - Include: theme, language, defaultSearchSource, enableStreaming
  - Add persist middleware for localStorage
  - Create `frontend/lib/stores/index.ts` barrel export

  **Must NOT do**:
  - Don't add auth state (use existing AuthContext)
  - Don't add search history state (fetch on demand)

  **Parallelizable**: NO (depends on 1)

  **References**:
  **Pattern References**:
  - `frontend/lib/auth/auth-context.tsx:1-116` - Existing state management pattern

  **API References**:
  - `backend/app/api/preferences.py:15-25` - PreferencesUpdate schema fields:
    - theme: light/dark/system
    - language: tr/en/ar
    - default_search_source: quran/bible/all
    - default_bible_testament: ot/nt/apocrypha/all
    - results_per_page: 5-50
    - enable_streaming: boolean
    - enable_multi_agent: boolean

  **Acceptance Criteria**:
  - [ ] File exists: `frontend/lib/stores/preferences-store.ts`
  - [ ] Store exports: `usePreferencesStore` hook
  - [ ] Store has actions: `setTheme`, `setLanguage`, `fetchPreferences`, `savePreferences`
  - [ ] `localStorage.getItem('preferences-storage')` → persisted state

  **Manual Verification**:
  - [ ] Browser console: `localStorage.setItem('test', 'ok')` → no errors

  **Commit**: YES
  - Message: `feat(frontend): add zustand preferences store with persistence`
  - Files: `frontend/lib/stores/preferences-store.ts`, `frontend/lib/stores/index.ts`

---

- [x] 3. Create SSE streaming hook

  **What to do**:
  - Create `frontend/lib/hooks/use-sse.ts`
  - Support both `/api/stream/search` and `/api/stream/compare`
  - Handle connection, message parsing, error, and close events
  - Return: { data, isStreaming, error, startStream, stopStream }

  **Must NOT do**:
  - Don't modify existing pages yet (task 11-12)
  - Don't add WebSocket support

  **Parallelizable**: NO (depends on 2)

  **References**:
  **API References**:
  - `backend/app/api/stream.py` - SSE endpoints:
    - `GET /api/stream/search?q={query}&source=quran|bible`
    - `GET /api/stream/compare?topic={topic}`

  **Pattern References**:
  - `frontend/app/search/page.tsx:41-71` - Current fetch pattern to replace

  **External References**:
  - MDN EventSource API: https://developer.mozilla.org/en-US/docs/Web/API/EventSource

  **Acceptance Criteria**:
  - [ ] File exists: `frontend/lib/hooks/use-sse.ts`
  - [ ] Hook exports: `useSSE` with TypeScript types
  - [ ] Handles: connection open, message, error, close events
  - [ ] Returns: `{ data, isStreaming, error, startStream, stopStream }`

  **Manual Verification**:
  - [ ] Import test in any page: `import { useSSE } from '@/lib/hooks/use-sse'` → no errors

  **Commit**: YES
  - Message: `feat(frontend): add SSE streaming hook for real-time responses`
  - Files: `frontend/lib/hooks/use-sse.ts`

---

- [x] 4. Create Global Navigation component

  **What to do**:
  - Create `frontend/components/layout/navigation.tsx`
  - Include: Logo, Search (Quran/Bible dropdown), Browse (Quran/Bible dropdown), Compare, History, User dropdown (Settings, Logout)
  - Responsive: Mobile hamburger menu
  - Highlight current page
  - Update `frontend/app/layout.tsx` to include Navigation

  **Must NOT do**:
  - Don't add theme toggle
  - Don't add notification bell/icon

  **Parallelizable**: NO (depends on 3)

  **References**:
  **Pattern References**:
  - `frontend/app/search/page.tsx:84-114` - Current inline header pattern
  - `frontend/app/compare/page.tsx:122-153` - Similar header pattern
  - `frontend/lib/design-system.ts:1-23` - Spring presets and color tokens

  **Component References**:
  - `frontend/components/ui/button.tsx` - Button component
  - `frontend/components/ui/dropdown-menu.tsx` - Dropdown menu

  **Auth References**:
  - `frontend/lib/auth/auth-context.tsx:109-115` - useAuth hook usage

  **Acceptance Criteria**:
  - [ ] File exists: `frontend/components/layout/navigation.tsx`
  - [ ] Navigation shows on all authenticated pages
  - [ ] Links: Search, Search Bible, Quran, Bible, Compare, History, Settings
  - [ ] User dropdown: user name/email, Settings link, Logout button
  - [ ] Current page highlighted
  - [ ] Mobile: Hamburger menu works

  **Manual Verification**:
  - [ ] Using Playwright browser:
    - Navigate to: `http://localhost:3000/search`
    - Verify: Navigation bar visible at top
    - Click: "Compare" link → navigates to /compare
    - Click: User dropdown → shows Settings, Logout

  **Commit**: YES
  - Message: `feat(frontend): add global navigation component`
  - Files: `frontend/components/layout/navigation.tsx`, `frontend/app/layout.tsx`

---

- [x] 5. Setup Vitest + React Testing Library

  **What to do**:
  - Install: `npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom @vitejs/plugin-react`
  - Create `frontend/vitest.config.ts`
  - Create `frontend/vitest.setup.ts` with testing-library matchers
  - Add `test` script to package.json
  - Create example test: `frontend/__tests__/example.test.tsx`

  **Must NOT do**:
  - Don't add Playwright E2E setup
  - Don't add Storybook
  - Don't add visual regression testing

  **Parallelizable**: NO (depends on 4)

  **References**:
  **Config References**:
  - `frontend/package.json` - Add test scripts and devDependencies
  - `frontend/tsconfig.json` - May need test includes

  **External References**:
  - Vitest Next.js setup: https://nextjs.org/docs/app/building-your-application/testing/vitest
  - Testing Library React: https://testing-library.com/docs/react-testing-library/intro

  **Acceptance Criteria**:
  - [ ] File exists: `frontend/vitest.config.ts`
  - [ ] File exists: `frontend/vitest.setup.ts`
  - [ ] File exists: `frontend/__tests__/example.test.tsx`
  - [ ] `npm test` → runs vitest, 1 test passes
  - [ ] `package.json` has `"test": "vitest"` script

  **Manual Verification**:
  - [ ] Terminal: `cd frontend && npm test` → "1 passed"

  **Commit**: YES
  - Message: `feat(frontend): setup vitest and react testing library`
  - Files: `frontend/vitest.config.ts`, `frontend/vitest.setup.ts`, `frontend/__tests__/example.test.tsx`, `frontend/package.json`

---

### PAGE PHASE (Parallelizable)

- [ ] 6. Refactor Search page with 4-tab interface

  **What to do**:
  - Create component: `frontend/components/search/search-tabs.tsx`
  - Update page: `frontend/app/search/page.tsx`
  - Add 4 tabs: Kuran | Eski Ahit | Yeni Ahit | Apokrifa
  - Each tab calls appropriate API endpoint:
    - Kuran → `/api/search/quran`
    - Eski Ahit → `/api/search/bible` with `testament: "ot"`
    - Yeni Ahit → `/api/search/bible` with `testament: "nt"`
    - Apokrifa → `/api/search/bible` with `testament: "apocrypha"`
  - Persist selected tab in URL query param (?source=quran|ot|nt|apocrypha)
  - Create test: `frontend/__tests__/search-tabs.test.tsx`

  **Must NOT do**:
  - Don't add SSE streaming yet (task 11)
  - Don't create separate pages per testament

  **Parallelizable**: YES (with 7, 8, 9, 10)

  **References**:
  **Pattern References**:
  - `frontend/app/search/page.tsx:1-179` - Current search page to refactor
  - `frontend/app/compare/page.tsx:266-279` - Expandable section pattern

  **API References**:
  - `backend/app/api/search.py` - Search endpoints
  - Quran: `POST /api/search/quran` - Body: `{ query, mode: "semantic", top_k: 10 }`
  - Bible: `POST /api/search/bible` - Body: `{ query, mode: "semantic", top_k: 10, testament: "ot"|"nt"|"apocrypha" }`

  **Component References**:
  - `frontend/components/ui/glow-card.tsx` - Result cards
  - `frontend/components/ui/button.tsx` - Tab buttons

  **Acceptance Criteria**:
  - [ ] Component file: `frontend/components/search/search-tabs.tsx`
  - [ ] Test file: `frontend/__tests__/search-tabs.test.tsx`
  - [ ] `npm test search-tabs` → passes
  - [ ] 4 tabs visible and clickable
  - [ ] URL updates on tab switch (?source=ot)
  - [ ] Results show appropriate format per source

  **Manual Verification**:
  - [ ] Using Playwright browser:
    - Navigate to: `http://localhost:3000/search`
    - Verify: 4 tabs visible (Kuran | Eski Ahit | Yeni Ahit | Apokrifa)
    - Click: "Eski Ahit" tab
    - Verify: URL shows `?source=ot`
    - Type: "love your neighbor" in search box
    - Click: Search button
    - Verify: Results show OT book references
    - Click: "Kuran" tab
    - Type: "sabır" in search box
    - Click: Search
    - Verify: Results show Surah:Ayet format

  **Commit**: YES
  - Message: `feat(frontend): add 4-tab search interface for all scriptures`
  - Files: `frontend/app/search/page.tsx`, `frontend/components/search/search-tabs.tsx`, `frontend/__tests__/search-tabs.test.tsx`

---

- [x] 7. Create Search History page with test

  **What to do**:
  - Create test: `frontend/__tests__/history.test.tsx`
  - Create page: `frontend/app/history/page.tsx`
  - Fetch from `/api/search/history` with pagination
  - Display: query, type (quran/bible), timestamp, result count
  - Add delete button per item
  - Add "Clear All" button

  **Must NOT do**:
  - Don't add re-run search functionality
  - Don't add filtering by type

  **Parallelizable**: YES (with 6, 8, 9, 10)

  **References**:
  **Pattern References**:
  - `frontend/app/search/page.tsx:1-179` - Page structure pattern
  - `frontend/app/compare/page.tsx:254-321` - List rendering with animation

  **API References**:
  - Endpoint: `GET /api/search/history?page=1&per_page=20`
  - Response: `{ items: [...], total, page, per_page, pages }`
  - Delete: `DELETE /api/search/history/{id}`

  **Component References**:
  - `frontend/components/ui/glow-card.tsx` - History item cards
  - `frontend/components/ui/button.tsx` - Delete buttons

  **Acceptance Criteria**:
  - [ ] Test file: `frontend/__tests__/history.test.tsx`
  - [ ] Page file: `frontend/app/history/page.tsx`
  - [ ] `npm test history` → passes
  - [ ] Pagination works (next/prev buttons)
  - [ ] Delete single item works
  - [ ] Empty state shows message

  **Manual Verification**:
  - [ ] Using Playwright browser:
    - Navigate to: `http://localhost:3000/history`
    - Verify: List of past searches displayed
    - Click: Delete button on first item
    - Verify: Item removed from list
    - Verify: Empty state if no history

  **Commit**: YES
  - Message: `feat(frontend): add search history page with delete functionality`
  - Files: `frontend/app/history/page.tsx`, `frontend/__tests__/history.test.tsx`

---

- [x] 8. Create User Preferences page with test

  **What to do**:
  - Create test: `frontend/__tests__/settings.test.tsx`
  - Create page: `frontend/app/settings/page.tsx`
  - Fetch current preferences from `/api/preferences/`
  - Display form with: language (TR/EN/AR), theme (Light/Dark/System), default source, results per page, streaming toggle
  - Save button calls `PUT /api/preferences/`
  - Reset button calls `DELETE /api/preferences/`
  - Sync with Zustand store

  **Must NOT do**:
  - Don't add profile editing (name, password) - backend doesn't support
  - Don't add avatar upload
  - Don't add account deletion

  **Parallelizable**: YES (with 6, 7, 9, 10)

  **References**:
  **Pattern References**:
  - `frontend/app/login/page.tsx:36-113` - Form pattern with GlowCard

  **API References**:
  - `backend/app/api/preferences.py:15-25` - PreferencesUpdate fields:
    - theme: light/dark/system
    - language: tr/en/ar
    - default_search_source: quran/bible/all
    - default_bible_testament: ot/nt/apocrypha/all
    - results_per_page: 5-50
    - enable_streaming: boolean
    - enable_multi_agent: boolean
  - Endpoint: `GET /api/preferences/` - Fetch current
  - Endpoint: `PUT /api/preferences/` - Update
  - Endpoint: `DELETE /api/preferences/` - Reset to defaults

  **Store References**:
  - `frontend/lib/stores/preferences-store.ts` - Zustand store (created in task 2)

  **Acceptance Criteria**:
  - [ ] Test file: `frontend/__tests__/settings.test.tsx`
  - [ ] Page file: `frontend/app/settings/page.tsx`
  - [ ] `npm test settings` → passes
  - [ ] Form loads current preferences
  - [ ] Save button updates preferences
  - [ ] Reset button restores defaults
  - [ ] Zustand store synced

  **Manual Verification**:
  - [ ] Using Playwright browser:
    - Navigate to: `http://localhost:3000/settings`
    - Verify: Current preferences loaded in form
    - Change: Language to "English"
    - Click: Save button
    - Refresh: Page
    - Verify: Language still shows "English"
    - Click: Reset to Defaults
    - Verify: Form resets to default values

  **Commit**: YES
  - Message: `feat(frontend): add user preferences page with sync to backend`
  - Files: `frontend/app/settings/page.tsx`, `frontend/__tests__/settings.test.tsx`

---

- [x] 9. Create Quran Browse page with test

  **What to do**:
  - Create test: `frontend/__tests__/quran.test.tsx`
  - Create page: `frontend/app/quran/page.tsx`
  - Fetch all surahs from `/api/metadata/quran/surahs`
  - Display: Surah number, Arabic name, Transliterated name, verse count
  - Click surah → navigate to `/search?surah={id}`
  - Add search/filter by surah name

  **Must NOT do**:
  - Don't show verses inline
  - Don't add Arabic font optimization

  **Parallelizable**: YES (with 6, 7, 8, 10)

  **References**:
  **Pattern References**:
  - `frontend/app/search/page.tsx:151-174` - Results list with animation

  **API References**:
  - Endpoint: `GET /api/metadata/quran/surahs`
  - Response: Array of `{ id, name, name_transliterated, verse_count, revelation_type }`

  **Component References**:
  - `frontend/components/ui/glow-card.tsx` - Surah cards
  - `frontend/components/ui/input.tsx` - Filter input

  **Acceptance Criteria**:
  - [ ] Test file: `frontend/__tests__/quran.test.tsx`
  - [ ] Page file: `frontend/app/quran/page.tsx`
  - [ ] `npm test quran` → passes
  - [ ] All 114 surahs displayed
  - [ ] Filter by name works
  - [ ] Click surah → navigates to search with filter

  **Manual Verification**:
  - [ ] Using Playwright browser:
    - Navigate to: `http://localhost:3000/quran`
    - Verify: 114 surahs listed
    - Type: "Fatiha" in filter
    - Verify: Only Al-Fatiha shown
    - Click: Al-Fatiha card
    - Verify: Navigated to `/search?surah=1`

  **Commit**: YES
  - Message: `feat(frontend): add quran browse page with surah listing`
  - Files: `frontend/app/quran/page.tsx`, `frontend/__tests__/quran.test.tsx`

---

- [x] 10. Create Old Testament Browse page with test

  **What to do**:
  - Create test: `frontend/__tests__/old-testament.test.tsx`
  - Create page: `frontend/app/old-testament/page.tsx`
  - Fetch OT books from `/api/metadata/bible/books?testament=ot`
  - Display: Book name (English + Hebrew), chapter count
  - Click book → navigate to `/search?source=ot&book={nr}`
  - Add search/filter by book name

  **Must NOT do**:
  - Don't show chapters inline
  - Don't mix with other testaments

  **Parallelizable**: YES (with 6, 7, 8, 9, 10a, 10b)

  **References**:
  **Pattern References**:
  - `frontend/app/quran/page.tsx` - Similar browse pattern (created in task 9)

  **API References**:
  - Endpoint: `GET /api/metadata/bible/books?testament=ot`
  - Response: Array of `{ nr, name, chapter_count, testament }`
  - Expected: 39 books (Genesis to Malachi)

  **Component References**:
  - `frontend/components/ui/glow-card.tsx` - Book cards
  - `frontend/components/ui/input.tsx` - Filter input

  **Acceptance Criteria**:
  - [ ] Test file: `frontend/__tests__/old-testament.test.tsx`
  - [ ] Page file: `frontend/app/old-testament/page.tsx`
  - [ ] `npm test old-testament` → passes
  - [ ] 39 OT books displayed
  - [ ] Filter by name works
  - [ ] Click book → navigates to search

  **Manual Verification**:
  - [ ] Using Playwright browser:
    - Navigate to: `http://localhost:3000/old-testament`
    - Verify: 39 OT books listed (Genesis to Malachi)
    - Type: "Genesis" in filter
    - Verify: Only Genesis shown
    - Click: Genesis card
    - Verify: Navigated to `/search?source=ot&book=1`

  **Commit**: YES
  - Message: `feat(frontend): add old testament browse page`
  - Files: `frontend/app/old-testament/page.tsx`, `frontend/__tests__/old-testament.test.tsx`

---

- [x] 10a. Create New Testament Browse page with test

  **What to do**:
  - Create test: `frontend/__tests__/new-testament.test.tsx`
  - Create page: `frontend/app/new-testament/page.tsx`
  - Fetch NT books from `/api/metadata/bible/books?testament=nt`
  - Display: Book name, chapter count
  - Click book → navigate to `/search?source=nt&book={nr}`
  - Add search/filter by book name

  **Must NOT do**:
  - Don't show chapters inline
  - Don't mix with other testaments

  **Parallelizable**: YES (with 6, 7, 8, 9, 10, 10b)

  **References**:
  **Pattern References**:
  - `frontend/app/old-testament/page.tsx` - Copy this pattern (created in task 10)

  **API References**:
  - Endpoint: `GET /api/metadata/bible/books?testament=nt`
  - Response: Array of `{ nr, name, chapter_count, testament }`
  - Expected: 27 books (Matthew to Revelation)

  **Acceptance Criteria**:
  - [ ] Test file: `frontend/__tests__/new-testament.test.tsx`
  - [ ] Page file: `frontend/app/new-testament/page.tsx`
  - [ ] `npm test new-testament` → passes
  - [ ] 27 NT books displayed
  - [ ] Filter by name works

  **Manual Verification**:
  - [ ] Using Playwright browser:
    - Navigate to: `http://localhost:3000/new-testament`
    - Verify: 27 NT books listed (Matthew to Revelation)
    - Click: Matthew card
    - Verify: Navigated to `/search?source=nt&book=40`

  **Commit**: YES
  - Message: `feat(frontend): add new testament browse page`
  - Files: `frontend/app/new-testament/page.tsx`, `frontend/__tests__/new-testament.test.tsx`

---

- [x] 10b. Create Apocrypha Browse page with test

  **What to do**:
  - Create test: `frontend/__tests__/apocrypha.test.tsx`
  - Create page: `frontend/app/apocrypha/page.tsx`
  - Fetch Apocrypha books from `/api/metadata/bible/books?testament=apocrypha`
  - Display: Book name, chapter count
  - Click book → navigate to `/search?source=apocrypha&book={nr}`
  - Add search/filter by book name

  **Must NOT do**:
  - Don't show chapters inline
  - Don't mix with other testaments

  **Parallelizable**: YES (with 6, 7, 8, 9, 10, 10a)

  **References**:
  **Pattern References**:
  - `frontend/app/old-testament/page.tsx` - Copy this pattern (created in task 10)

  **API References**:
  - Endpoint: `GET /api/metadata/bible/books?testament=apocrypha`
  - Response: Array of `{ nr, name, chapter_count, testament }`
  - Expected: ~15 books (varies by canon)

  **Acceptance Criteria**:
  - [ ] Test file: `frontend/__tests__/apocrypha.test.tsx`
  - [ ] Page file: `frontend/app/apocrypha/page.tsx`
  - [ ] `npm test apocrypha` → passes
  - [ ] Apocrypha books displayed
  - [ ] Filter by name works

  **Manual Verification**:
  - [ ] Using Playwright browser:
    - Navigate to: `http://localhost:3000/apocrypha`
    - Verify: Apocrypha books listed
    - Click: Any book card
    - Verify: Navigated to `/search?source=apocrypha&book={nr}`

  **Commit**: YES
  - Message: `feat(frontend): add apocrypha browse page`
  - Files: `frontend/app/apocrypha/page.tsx`, `frontend/__tests__/apocrypha.test.tsx`

---

### INTEGRATION PHASE

- [ ] 11. Add SSE streaming to Search page

  **What to do**:
  - Update `frontend/app/search/page.tsx`
  - Import and use `useSSE` hook from task 3
  - Show streaming tokens as they arrive (typewriter effect)
  - Add toggle for streaming vs. batch mode
  - Fallback to regular fetch if SSE fails

  **Must NOT do**:
  - Don't change the visual design
  - Don't remove existing functionality

  **Parallelizable**: NO (depends on 6-10)

  **References**:
  **Hook References**:
  - `frontend/lib/hooks/use-sse.ts` - SSE hook (created in task 3)

  **Page References**:
  - `frontend/app/search/page.tsx:41-71` - Replace this fetch with SSE

  **API References**:
  - `GET /api/stream/search?q={query}&source=quran`

  **Acceptance Criteria**:
  - [ ] Tokens appear one by one (typewriter effect)
  - [ ] Streaming toggle visible (from preferences)
  - [ ] Fallback to batch mode on error
  - [ ] Existing tests still pass

  **Manual Verification**:
  - [ ] Using Playwright browser:
    - Navigate to: `http://localhost:3000/search`
    - Type: "sabır" in search box
    - Click: Search
    - Verify: Results appear progressively (not all at once)
    - Toggle: Streaming off in settings
    - Search: Again
    - Verify: Results appear all at once

  **Commit**: YES
  - Message: `feat(frontend): add SSE streaming to quran search`
  - Files: `frontend/app/search/page.tsx`

---

- [ ] 12. Add SSE streaming to Compare page

  **What to do**:
  - Update `frontend/app/compare/page.tsx`
  - Import and use `useSSE` hook
  - Stream paragraphs as they complete
  - Show progress indicator per agent

  **Must NOT do**:
  - Don't change the 5-paragraph structure
  - Don't remove citation display

  **Parallelizable**: NO (depends on 11)

  **References**:
  **Hook References**:
  - `frontend/lib/hooks/use-sse.ts` - SSE hook

  **Page References**:
  - `frontend/app/compare/page.tsx:76-109` - Replace this fetch with SSE

  **API References**:
  - `GET /api/stream/compare?topic={topic}`

  **Acceptance Criteria**:
  - [ ] Paragraphs appear as agents complete
  - [ ] Progress shown per agent
  - [ ] Final result matches batch mode
  - [ ] Existing tests still pass

  **Manual Verification**:
  - [ ] Using Playwright browser:
    - Navigate to: `http://localhost:3000/compare`
    - Type: "patience" in topic box
    - Click: Analyze
    - Verify: Paragraphs appear one by one
    - Verify: Agent progress indicators shown

  **Commit**: YES
  - Message: `feat(frontend): add SSE streaming to compare page`
  - Files: `frontend/app/compare/page.tsx`

---

### FINALIZATION PHASE

- [ ] 13. Final verification and cleanup

  **What to do**:
  - Run all tests: `npm test`
  - Run build: `npm run build`
  - Test all pages manually in browser
  - Verify navigation works on all pages
  - Remove any console.log statements
  - Update memory-bank/progress.md

  **Must NOT do**:
  - Don't add new features
  - Don't refactor working code

  **Parallelizable**: NO (final task)

  **References**:
  **All new files created in this plan**

  **Acceptance Criteria**:
  - [ ] `npm test` → All tests pass
  - [ ] `npm run build` → No errors
  - [ ] All 5 new pages accessible
  - [ ] Navigation visible on all authenticated pages
  - [ ] SSE streaming works on Search and Compare
  - [ ] No console errors in browser

  **Manual Verification**:
  - [ ] Using Playwright browser:
    - Navigate through all pages: /, /login, /register, /search, /search-bible, /quran, /bible, /compare, /history, /settings
    - Verify: No broken links
    - Verify: No console errors
    - Verify: Navigation consistent

  **Commit**: YES
  - Message: `chore(frontend): final cleanup and verification`
  - Files: `memory-bank/progress.md`, any cleanup files

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `feat(frontend): add zustand` | package.json | npm ls zustand |
| 2 | `feat(frontend): add preferences store` | lib/stores/* | import test |
| 3 | `feat(frontend): add SSE hook` | lib/hooks/* | import test |
| 4 | `feat(frontend): add navigation` | components/layout/*, layout.tsx | visual check |
| 5 | `feat(frontend): setup vitest` | vitest.*, tests/* | npm test |
| 6 | `feat(frontend): 4-tab search interface` | app/search/*, components/search/*, tests/* | npm test |
| 7 | `feat(frontend): history page` | app/history/*, tests/* | npm test |
| 8 | `feat(frontend): settings page` | app/settings/*, tests/* | npm test |
| 9 | `feat(frontend): quran browse page` | app/quran/*, tests/* | npm test |
| 10 | `feat(frontend): old testament browse` | app/old-testament/*, tests/* | npm test |
| 10a | `feat(frontend): new testament browse` | app/new-testament/*, tests/* | npm test |
| 10b | `feat(frontend): apocrypha browse` | app/apocrypha/*, tests/* | npm test |
| 11 | `feat(frontend): SSE search` | app/search/page.tsx | manual verify |
| 12 | `feat(frontend): SSE compare` | app/compare/page.tsx | manual verify |
| 13 | `chore(frontend): final cleanup` | progress.md | full test |

---

## Success Criteria

### Verification Commands
```bash
cd frontend
npm test        # All tests pass
npm run build   # No errors
npm run dev     # Server starts
```

### Final Checklist
- [ ] Search page has 4 tabs (Kuran | Eski Ahit | Yeni Ahit | Apokrifa)
- [ ] All 4 browse pages present (/quran, /old-testament, /new-testament, /apocrypha)
- [ ] History page functional
- [ ] Settings page functional
- [ ] Global navigation on all authenticated pages
- [ ] SSE streaming working on Search and Compare
- [ ] All tests passing
- [ ] Build successful
- [ ] No console errors
- [ ] Memory bank updated
