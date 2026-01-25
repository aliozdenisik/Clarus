# Active Context

## Current Work Focus

**Date**: 2026-01-25

**Constraint**: Delegation System Failure (2026-01-24) - `delegate_task(run_in_background=false)` fails. Strategy: Execute synchronous tasks directly.

**Rebranding Complete** - Project rebranded from "Sacred Texts Search" to "Clarus".

## Recent Changes

### Rebranding to Clarus (2026-01-25)

Project rebranded from "Sacred Texts Search" to "Clarus":

**Documentation:**
- README.md - Project title
- memory-bank/projectbrief.md - Project title
- memory-bank/productContext.md - UI references

**Frontend:**
- package.json - App name
- app/layout.tsx - Metadata title
- app/page.tsx - Landing page title
- components/layout/navigation.tsx - Logo text
- app/search/page.tsx - Page heading
- messages/en.json - i18n strings
- messages/tr.json - i18n strings

**Backend:**
- backend/src/__init__.py - Package comment
- backend/app/main.py - FastAPI title & description
- backend/main.py - CLI docstring & argparse description

### Frontend Development Complete (2026-01-24)

Next.js 15 + Framer Motion ile modern frontend tamamlandi:

**Sayfalar:**
- `/` - Landing page (Sign In / Get Started)
- `/login` - JWT authentication
- `/register` - User registration
- `/search` - Kuran semantic search
- `/compare` - Multi-agent karsilastirmali analiz (CLI ciktisi gibi)

**Ozellikler:**
- Linear-style dark theme design system
- Spring animations (Framer Motion)
- GlowCard components
- Real-time search results
- 5-paragraph structured analysis display
- Citations badges per source
- Responsive layout

**Browser Test Results:**
- Login/Register: ✅ Calisiyor
- Search: ✅ 10 sonuc, skorlarla gosterim
- Compare: ✅ 80 verses → 5 paragraphs → 32 citations → %95 confidence

### User Preferences Page (2026-01-25)

- Implemented `/settings` with Zustand store integration
- Full form support for all 7 preference fields
- Validated with TDD (5 tests passing)

### Apocrypha Browse Page (2026-01-25)

- Implemented `/apocrypha` with book listing and filtering
- Copied pattern from Old Testament page
- Validated with TDD (4 tests passing)

### Backend Compare API Fix (2026-01-24)

`MultiAgentAnswer` serialization hatasi duzeltildi:

**Onceki (Hatali):**
```python
analysis=result.full_text if hasattr(result, 'full_text') else str(result)
```

**Sonraki (Dogru):**
```python
essay=result.to_essay()
paragraphs=[ParagraphData(...) for each commentary]
citations=result.citations
```

**Yeni CompareResponse Schema:**
```python
class CompareResponse:
    topic: str
    essay: str                      # Full markdown essay
    paragraphs: List[ParagraphData] # 5 structured paragraphs
    citations: Dict[str, List[str]] # Grouped by source
    confidence: float
    total_verses: int
    total_citations: int
    latency_ms: int
```

### Qdrant Persistence Fix (2026-01-25)

- **Root Cause**: Docker Desktop 4.55.0 bind mount sync issue
- **Solution**: Switched from bind mount (`./qdrant_data`) to named volume (`qdrant_storage`)
- **Verification**: All 43,055 vectors preserved across restart
- **Collections**: quran_tr (6,236), bible_ot (23,145), bible_nt (7,957), bible_apocrypha (5,717)

### New/Modified Files
- `frontend/app/compare/page.tsx` - Compare sayfasi (yeni)
- `frontend/app/search/page.tsx` - Compare butonu eklendi
- `backend/app/api/compare.py` - Rich response schema
- `test-credentials.json` - Browser test kullanicisi
- `.gitignore` - test-credentials.json eklendi

### Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15 + Framer Motion |
| CLI | argparse + Rich |
| Backend | FastAPI + SQLAlchemy |
| Auth | JWT + Google OAuth |
| Database | PostgreSQL |
| Vector DB | Qdrant |

### Testament Collections

| Collection | Points | Agent |
|------------|--------|-------|
| `quran_tr` | 6,236 | QuranAgent |
| `bible_ot` | 23,145 | OldTestamentAgent |
| `bible_nt` | 7,957 | NewTestamentAgent |
| `bible_apocrypha` | 5,717 | ApocryphaAgent |

## Next Steps

1. **Production Readiness**
   - Docker production build
   - HTTPS configuration
   - Google OAuth credentials setup

2. **Frontend Enhancements**
   - Bible search page
   - User preferences page
   - Search history page

3. **Optional Enhancements**
   - Arabic font optimization
   - Batch query API
   - WebSocket support for real-time chat

## Active Decisions

- **Rate Limit**: 50 queries/day/user
- **Language**: Turkish (Quran), English (Bible)
- **Primary Interface**: Web App + CLI
- **Frontend Framework**: Next.js 15 (App Router)

## Test Credentials

Browser testleri icin kullanilir (`.gitignore`'da):
```json
{
  "email": "browser-test@example.com",
  "password": "Test1234!",
  "name": "Browser Test"
}
```

## Learnings

1. **Next.js 15** App Router + Framer Motion iyi calisiyor
2. **FastAPI + SQLAlchemy async** handles concurrent requests efficiently
3. **SSE streaming** provides good UX for long-running LLM calls
4. **Semantic LLM Cache** significantly reduces API costs (60-80%)
5. **MultiAgentAnswer.to_essay()** metodu API serialization icin kullanilmali
