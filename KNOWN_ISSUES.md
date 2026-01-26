# Known Issues & Required Fixes

**Last Updated:** 2026-01-26  
**Status:** Active Development

---

## Critical Issues (MUST FIX)

### 1. Backend Process Hangs Under Load

**Severity:** HIGH  
**Status:** WORKAROUND AVAILABLE  
**Affected:** `backend/app/main.py` (uvicorn)

**Symptom:**
- Backend stops responding to ALL requests
- Frontend shows infinite "Loading..." state
- `curl http://localhost:8000/api/auth/me --max-time 5` times out
- Process is running (`lsof -i :8000`) but not responding

**Root Cause:**
- Unknown - possibly async event loop blocking or resource exhaustion
- Occurs randomly, not tied to specific requests

**Current Workaround:**
```bash
pkill -9 -f "uvicorn"
cd backend && source ../venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Recommended Fixes:**

1. **Add Health Check Endpoint with Watchdog**
   ```python
   # backend/app/api/health.py
   from fastapi import APIRouter
   import asyncio
   
   router = APIRouter()
   
   @router.get("/health")
   async def health_check():
       # Add timeout to detect hung event loop
       try:
           await asyncio.wait_for(asyncio.sleep(0.1), timeout=1.0)
           return {"status": "healthy"}
       except asyncio.TimeoutError:
           return {"status": "unhealthy", "reason": "event_loop_blocked"}
   ```

2. **Add Process Supervisor (systemd/supervisord)**
   ```ini
   # /etc/supervisor/conf.d/clarus.conf
   [program:clarus-backend]
   command=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   directory=/path/to/backend
   autostart=true
   autorestart=true
   startsecs=10
   stopwaitsecs=10
   ```

3. **Add Uvicorn Timeout Configuration**
   ```bash
   uvicorn app.main:app --timeout-keep-alive 30 --timeout-notify 30
   ```

4. **Frontend: Add Backend Health Check Before Critical Operations**
   ```typescript
   // frontend/lib/api/health.ts
   export async function checkBackendHealth(): Promise<boolean> {
     try {
       const response = await fetch('/api/health', { 
         signal: AbortSignal.timeout(5000) 
       });
       return response.ok;
     } catch {
       return false;
     }
   }
   ```

---

### 2. SSE Streaming Connection Drops

**Severity:** MEDIUM  
**Status:** FALLBACK EXISTS (working)  
**Affected:** `frontend/app/compare/page.tsx`, `backend/app/api/stream.py`

**Symptom:**
- Toast: "Streaming connection lost. Falling back to standard analysis..."
- SSE connection (`/api/stream/compare`) terminates unexpectedly

**Current Behavior:**
1. Frontend attempts SSE streaming first
2. On failure, automatically falls back to standard POST (`/api/compare/`)
3. Results return successfully via fallback
4. User sees warning toast but gets correct results

**Root Cause:**
- SSE connections are fragile over proxies/load balancers
- Browser may close idle connections
- Network interruptions during long-running analysis (~40s)

**Recommended Fixes:**

1. **Add SSE Heartbeat/Keep-Alive**
   ```python
   # backend/app/api/stream.py
   async def stream_compare(query: str):
       async def event_generator():
           last_heartbeat = time.time()
           async for chunk in compare_generator(query):
               yield f"data: {json.dumps(chunk)}\n\n"
               
               # Send heartbeat every 10 seconds
               if time.time() - last_heartbeat > 10:
                   yield f": heartbeat\n\n"
                   last_heartbeat = time.time()
       
       return EventSourceResponse(event_generator())
   ```

2. **Frontend: Add Reconnection Logic**
   ```typescript
   // frontend/lib/hooks/use-sse.ts
   const MAX_RETRIES = 3;
   let retryCount = 0;
   
   eventSource.onerror = () => {
     if (retryCount < MAX_RETRIES) {
       retryCount++;
       setTimeout(() => reconnect(), 1000 * retryCount);
     } else {
       fallbackToPost();
     }
   };
   ```

3. **Add Connection Timeout Configuration**
   ```typescript
   // frontend/lib/api/config.ts
   export const SSE_CONFIG = {
     timeout: 120000,  // 2 minutes max
     heartbeatInterval: 10000,
     maxRetries: 3,
   };
   ```

---

## Medium Priority Issues

### 3. No Graceful Shutdown Handling

**Severity:** MEDIUM  
**Status:** NOT IMPLEMENTED

**Problem:**
- Killing uvicorn with `pkill -9` may leave orphan processes
- In-flight requests are lost without notification
- Database connections may not close properly

**Recommended Fix:**
```python
# backend/app/main.py
import signal
import sys

def graceful_shutdown(signum, frame):
    logger.info("Received shutdown signal, cleaning up...")
    # Close database connections
    # Cancel pending tasks
    # Flush caches
    sys.exit(0)

signal.signal(signal.SIGTERM, graceful_shutdown)
signal.signal(signal.SIGINT, graceful_shutdown)
```

---

### 4. Frontend Auth State Depends on Backend Availability

**Severity:** MEDIUM  
**Status:** NOT IMPLEMENTED

**Problem:**
- If backend is down, frontend shows infinite loading
- No offline state or cached auth

**Recommended Fix:**
```typescript
// frontend/lib/auth/auth-context.tsx
useEffect(() => {
  const checkAuth = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch('/api/auth/me', { 
        signal: controller.signal 
      });
      clearTimeout(timeoutId);
      
      if (response.ok) {
        setUser(await response.json());
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        // Backend unreachable - show offline state
        setBackendStatus('offline');
      }
    } finally {
      setAuthLoading(false);
    }
  };
  
  checkAuth();
}, []);
```

---

## Low Priority / Nice to Have

### 5. No Request Retry Logic for LLM Calls

**Severity:** LOW  
**Status:** PARTIAL (some retries exist)

**Problem:**
- OpenRouter API calls can fail transiently
- No exponential backoff

**Recommended Fix:**
```python
# backend/src/llm_client.py
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_llm(prompt: str) -> str:
    ...
```

---

### 6. No Circuit Breaker for External Services

**Severity:** LOW  
**Status:** NOT IMPLEMENTED

**Problem:**
- If Qdrant or OpenRouter is down, requests pile up
- No fast-fail mechanism

**Recommended Fix:**
- Implement circuit breaker pattern using `pybreaker` or similar

---

## Environment-Specific Notes

### Development
- Backend may hang more frequently due to hot-reload
- Use `--reload` flag only in development

### Production Checklist
- [ ] Set up process supervisor (systemd/supervisord)
- [ ] Configure health check endpoint
- [ ] Set up monitoring/alerting for backend health
- [ ] Configure proper timeouts for all external calls
- [ ] Add circuit breakers for Qdrant and OpenRouter
- [ ] Set up log aggregation for debugging hangs

---

## Quick Reference: Recovery Commands

```bash
# Check if backend is responding
curl http://localhost:8000/api/auth/me --max-time 5

# Check what's using port 8000
lsof -i :8000

# Kill hung backend
pkill -9 -f "uvicorn"

# Restart backend
cd backend && source ../venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000

# Check Qdrant health
curl http://localhost:6333/health

# Check PostgreSQL
docker compose ps
```

---

## Related Files

- `.sisyphus/notepads/google-oauth/issues.md` - Original issue discovery notes
- `memory-bank/activeContext.md` - Current project context
- `backend/app/main.py` - FastAPI application entry point
- `frontend/app/compare/page.tsx` - SSE streaming implementation
