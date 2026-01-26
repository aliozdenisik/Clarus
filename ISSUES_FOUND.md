# Clarus - Known Issues & Bugs

**Last Updated:** 2026-01-26
**Status:** Active tracking document

---

## Test Summary

| Feature | Status | Notes |
|---------|--------|-------|
| User Registration | ✅ PASS | Works correctly |
| Compare Page Load | ✅ PASS | Page loads correctly |
| Multi-Agent Analysis | ✅ PASS | Analysis completes |
| Quran Verse Navigation | ✅ PASS | Links work: `/quran/{surahId}?verse={verseId}` |
| Bible Verse Navigation | ✅ PASS | Links work: `/bible/{bookNr}?chapter={chapter}&verse={verse}` |
| SSE Streaming | ⚠️ PARTIAL | Works but format mismatch causes fallback |
| Inline Citation Click | ✅ PASS | Scrolls to verse card with highlight |

---

## Active Issues

### 1. SSE Streaming Format Mismatch (Medium Priority)

**Severity:** MEDIUM  
**Status:** Not blocking - batch API fallback works  
**Location:** `backend/app/api/stream.py` + `frontend/lib/hooks/use-sse.ts`

**Symptom:**
- SSE streaming endpoint completes successfully (logs show `[COMPARE] Streaming completed successfully`)
- Frontend shows: "Streaming connection lost. Falling back to standard analysis..."
- Batch API fallback works correctly

**Root Cause:**
Format mismatch between backend and frontend SSE message formats:

| Backend sends | Frontend expects |
|---------------|------------------|
| `{"token": "word"}` | `{"type": "token", "content": "word"}` |
| `{"done": true}` | `{"type": "complete"}` |
| `{"verse_details": {...}}` | No type field expected |
| `{"status": "analyzing"}` | Not in SSEMessage interface |

Additionally, `EventSource.onerror` fires when connection closes (even normally after `done: true`), triggering fallback.

**Impact:**
- Users don't get real-time streaming experience
- Extra latency from fallback mechanism
- "Streaming connection lost" toast appears even on success

**Fix Options:**
1. **Option A**: Align backend to frontend format (modify `stream.py` to send `{"type": "token", "content": "..."}`)
2. **Option B**: Align frontend to backend format (modify `use-sse.ts` to accept current format)
3. **Option C**: Fix `onerror` handler to differentiate normal close from error

**Files to modify:**
- `backend/app/api/stream.py` - Change SSE event format
- `frontend/lib/hooks/use-sse.ts` - Update SSEMessage interface and handlers
- `frontend/app/compare/page.tsx` - Handle SSE data correctly

---

### 2. OpenRouter Rate Limiting (Low Priority)

**Severity:** LOW  
**Status:** Intermittent  
**Location:** `backend/src/multi_agent_answer_generator.py`

**Symptom:**
Backend logs show:
```
LLM call failed: 'choices'
LLM call failed: 429 Client Error: Too Many Requests for url: https://openrouter.ai/api/v1/chat/completions
```

**Root Cause:**
Multi-agent system runs 4 specialist agents in parallel, sometimes hitting OpenRouter rate limits.

**Impact:**
- Some agents return empty results (0 characters)
- Analysis quality may be reduced
- Overall result still generated with partial data

**Current Behavior:**
System handles this gracefully - generates summary with available agent outputs.

**Potential Fixes:**
1. Add exponential backoff retry for rate-limited calls
2. Stagger parallel agent calls with small delays
3. Implement per-request rate tracking

---

### 3. Verse Highlight Timing (Low Priority)

**Severity:** LOW  
**Status:** Minor UX issue  
**Location:** `frontend/app/quran/[surahId]/page.tsx`, `frontend/app/bible/[bookNr]/page.tsx`

**Symptom:**
When navigating to a verse via `?verse=N` query param, highlight may not be visible if:
- Page content hasn't loaded yet
- Scroll happens before verse element exists in DOM

**Impact:**
User may not see which verse was referenced.

**Potential Fix:**
Use `MutationObserver` or add loading state before attempting scroll/highlight.

---

## Resolved Issues

### Bible Verse Navigation Links (FIXED 2026-01-26)

**Previous Status:** Bible verses (OT, NT, Apocrypha) had no clickable links.

**Root Cause:** `book_nr` field was missing from API response despite being set in `VerseDetail` model.

**Fix Applied:**
1. Updated `VerseDetail` Pydantic model with `model_config` for proper serialization
2. Added `verse_details` event to SSE streaming endpoint
3. Implemented `navigateToVerse()` function in compare page

**Files Modified:**
- `backend/app/api/compare.py` - VerseDetail model fix
- `backend/app/api/stream.py` - Added verse_details SSE event
- `frontend/app/compare/page.tsx` - Added navigateToVerse function

**Verification:** Playwright tests confirm all 4 source types navigate correctly.

---

## Test Environment

- Backend: FastAPI on `localhost:8000`
- Frontend: Next.js 15 on `localhost:3000`
- Database: Qdrant on `localhost:6333` (43,055 vectors)
- LLM Provider: OpenRouter (Grok 4.1 Fast + Gemini 2.5 Flash)

---

## How to Test

```bash
# Start services
docker compose up -d
cd backend && uvicorn app.main:app --reload &
cd frontend && npm run dev &

# Run E2E test
cd frontend && npx playwright test

# Check backend logs
tail -f /tmp/backend.log
```
