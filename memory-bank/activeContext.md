# Active Context

## Current Work Focus

**Date**: 2026-01-27

**Completed**: 
- Reliability & Known Issues Fixes: Implemented circuit breakers, retry logic, SSE improvements, and offline handling.
- Test Coverage Improvements: Added 142 new tests across frontend and backend, achieving high coverage for critical reliability features.

### Reliability & Known Issues Fixes (2026-01-27)

Implemented comprehensive reliability improvements addressing 6 critical issues:

**Backend Improvements:**
- **Circuit Breaker Pattern** (pybreaker): Protects against Qdrant and OpenRouter failures
  - `qdrant_breaker`: fail_max=5, reset_timeout=60s
  - `llm_breaker`: fail_max=3, reset_timeout=30s
  - `embeddings_breaker`: fail_max=10, reset_timeout=120s
- **Tenacity Retry Decorators**: Exponential backoff on LLM calls (3 attempts, 2s→4s→8s)
- **Enhanced Health Check**: `/api/health` now returns event_loop status and Qdrant connectivity
- **Graceful Shutdown**: Proper cleanup in lifespan manager (5s timeout for DB/tasks)
- **SSE Heartbeats**: 4 heartbeat points in stream.py to prevent connection drops
- **systemd Service**: Template and install script at `backend/scripts/`

**Frontend Improvements:**
- **SSE Reconnection**: 3 retries with exponential backoff (1s→2s→4s)
- **Auth Timeout**: 10s AbortController timeout on auth check
- **Offline Banner**: Red banner when backend is unreachable
- **backendStatus State**: 'online' | 'offline' | 'unknown' in AuthContext

**New Files:**
- `backend/src/circuit_breaker.py` - Circuit breaker module
- `backend/scripts/systemd-install.sh` - Service installer
- `backend/scripts/clarus-backend.service.template` - Service template
- `frontend/components/layout/offline-banner.tsx` - Offline banner component

**Modified Files (14 total):**
- Backend: search.py, ultimate_rag.py, comparative_rag.py, query_enhancer.py, answer_generator.py, multi_agent_answer_generator.py, comparative_answer_generator.py, embeddings.py, app/main.py, app/api/stream.py
- Frontend: use-sse.ts, auth-context.tsx, providers.tsx

**Playwright Tests Verified:**
- Health check API: ✅ Returns healthy/degraded/unhealthy status
- SSE streaming: ✅ 80 verses returned across 4 sources
- Offline banner: ✅ Appears within 10s when backend down
- Online recovery: ✅ Banner disappears when backend restored

### Test Coverage Improvements (2026-01-27)
- Added 142 new tests (56 frontend, 76 backend unit tests, 10 extended auth tests).
- Verified reliability features: circuit breakers, health endpoints, and SSE reconnection.
- **Note**: Some pre-existing frontend tests are still failing. Refer to `ISSUES.md` for details on known test failures and resolution status.

## Recent Changes

### Google OAuth Integration (2026-01-26)

Frontend `AuthContext` updated to support Google OAuth login:

**Changes:**
- Added `loginWithGoogle(credential: string)` to `AuthContextType`.
- Implemented `loginWithGoogle` in `AuthProvider` using TDD.
- Function exchanges Google ID token for JWT via `/api/auth/google`.
- Tokens are stored in `localStorage` and `user` state is updated.
- Comprehensive error handling for network and backend errors.

**Test Results:**
- 5 new test cases added to `frontend/__tests__/auth-context.test.tsx`.
- All tests passed.

### Arabic Font Fix (2026-01-26)

Kuran ayetleri sayfasındaki bozuk Arapça görüntüleme düzeltildi:

**Problem:**
- Arapça harfler birleşmiyor, izole görünüyordu
- Harekeler (fatha, kasra, sukun) yanlış konumluydu
- Eksik glyph kutuları (□) görünüyordu
- Türkçe meal gösterilmiyordu

**Çözüm:**
- **Amiri** fontu eklendi (Google Fonts - klasik Arap kaligrafi tarzı)
- `.font-arabic` CSS sınıfı tanımlandı (RTL, line-height: 2)
- Türkçe çeviri her ayetin altında gösteriliyor
- Ayet numaraları büyütüldü (48px daire, 20px font)

**Değişen Dosyalar:**
- `frontend/app/layout.tsx` - Amiri font import
- `frontend/app/globals.css` - `.font-arabic` class
- `frontend/app/quran/[surahId]/page.tsx` - Verse interface + rendering

**Stil Değerleri:**
| Öğe | Değer |
|-----|-------|
| Arapça font | Amiri (Google Fonts) |
| Arapça boyut | `text-2xl` (24px) |
| Türkçe boyut | `text-2xl` (24px) |
| Türkçe renk | `--color-text-secondary` (#a1a1aa) |
| Ayet numarası | `h-12 w-12` daire, `text-xl` font |
| Satır aralığı | `line-height: 2` (harekeler için) |

**Commits:**
- `fix(frontend): add Arabic font support with Scheherazade New`
- `feat(frontend): display Turkish translation below Arabic verses`
- `style(frontend): increase translation and verse number sizes for better readability`
- `style(frontend): switch Arabic font from Scheherazade New to Amiri`

### Browse Detail Pages (2026-01-26)

Browse sayfalarından kitap/sure tıklandığında içerik görüntüleme sayfaları eklendi:

**Yeni Sayfalar:**
- `/quran/[surahId]/page.tsx` - Sure detay sayfası (Arapça ayetler)
- `/bible/[bookNr]/page.tsx` - Kitap detay sayfası (chapter seçimi + İngilizce ayetler)

**Özellikler:**
- **Quran Detay**: Sure başlığı (Arapça + transliterasyon), ayet listesi, "Back to Quran" navigasyon
- **Bible Detay**: Kitap başlığı, testament bilgisi, chapter seçim butonları, ayet listesi
- Chapter 1 otomatik yükleniyor
- Animasyonlu geçişler (Framer Motion)

**UI İyileştirmeleri:**
- `#67` gibi global kitap numaraları kaldırıldı (OT, NT, Apocrypha browse sayfalarından)
- Daha temiz kitap kartları (sadece isim + chapter sayısı)

**Düzenlenen Dosyalar:**
- `frontend/app/old-testament/page.tsx` - `#nr` kaldırıldı, `/bible/{nr}` yönlendirmesi
- `frontend/app/new-testament/page.tsx` - `#nr` kaldırıldı, `/bible/{nr}` yönlendirmesi
- `frontend/app/apocrypha/page.tsx` - `#nr` kaldırıldı, `/bible/{nr}` yönlendirmesi
- `frontend/app/quran/page.tsx` - `/quran/{id}` yönlendirmesi

**Backend API Kullanımı:**
- `GET /api/metadata/quran/surahs/{surah_id}` - Sure + ayetler
- `GET /api/metadata/bible/books/{book_nr}` - Kitap + chapter özeti
- `GET /api/metadata/bible/books/{book_nr}/chapters/{chapter_nr}` - Chapter + ayetler

**Test Sonuçları:**
- Quran: Al-Fatihah → 7 Arapça ayet ✅
- Bible: Genesis → Chapter 1 → 31 ayet ✅
- Console hatası yok ✅

### Compare Page Reference Enhancement (2026-01-26)

Compare sayfasına zengin kaynak referansları ve interaktif alıntılar eklendi:

**Backend Değişiklikleri:**
- `VerseDetail` Pydantic modeli eklendi (text, book_name, chapter, verse, source, translation)
- `verse_details: Optional[Dict[str, VerseDetail]]` field'ı CompareResponse'a eklendi
- `extract_quran_verse_detail()` ve `extract_bible_verse_detail()` helper fonksiyonları
- API response boyutu: 28KB (100KB limitinin altında)

**Frontend Bileşenleri (TDD ile):**
- `SourceBadge` - Kaynak renk badge'i (Kuran: Emerald, Eski Ahit: Blue, Yeni Ahit: Amber, Apokrifa: Purple)
- `SourceReferenceCard` - Ayet detayları kartı (badge + referans + çeviri + metin)
- `FilterTabs` - Kaynak filtreleme sekmeleri (Tümü, Kuran, Eski Ahit, Yeni Ahit, Apokrifa)
- `InlineCitation` - Tıklanabilir paragraf içi alıntılar

**Yeni Özellikler:**
- Tam ayet metinleri kaynak kartlarında görünür
- Kaynaklara göre filtreleme (20 ayet/kaynak)
- Paragraf içi `[Bakara:153]` alıntılarına tıklayınca ilgili karta scroll + 2sn highlight
- Çeviri bilgisi: "Diyanet Isleri Baskanligi" (Kuran), "King James Version with Apocrypha" (İncil)

**Test Sonuçları:**
- 71 test geçti (13 test dosyası)
- E2E browser testi başarılı
- Konsol hatası yok

**Dosyalar:**
- `backend/app/api/compare.py` - VerseDetail schema + helper functions
- `frontend/components/compare/` - 4 yeni bileşen
- `frontend/lib/utils/parse-citations.ts` - Citation parsing utility
- `frontend/__tests__/` - 5 yeni test dosyası (35 test)

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
