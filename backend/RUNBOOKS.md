# Clarus Operations Runbooks

Operational procedures for responding to Sentry alerts.

---

## error-rate-high

**Alert**: Error rate > 50 events/hour

### Symptoms
- Sentry dashboard shows spike in errors
- Users reporting failures
- API returning 500 errors
- Frontend displaying error toasts or "Something went wrong" messages

### Causes
1. **Database connectivity issues**: PostgreSQL at `localhost:54322` is down or unreachable.
2. **External API failures**: OpenRouter (LLM) or Qdrant (Vector DB) at `localhost:6333` returning errors.
3. **Code regression**: Recent deployments introducing bugs.
4. **Infrastructure problems**: Disk space, memory exhaustion, or network partitions.

### Resolution Steps
1. **Check error details in Sentry**
   - Open Sentry → Issues → Filter by time
   - Identify error type and stack trace

2. **Check service health**
   ```bash
   # Check API health
   curl http://localhost:8000/api/health
   # Check Docker services
   docker compose ps
   ```

3. **Check logs**
   ```bash
   docker compose logs --tail=100 api
   ```

4. **If Qdrant issue**:
   ```bash
   curl http://localhost:6333/healthz
   ```

5. **If OpenRouter issue**:
   - Check https://status.openrouter.ai/
   - Circuit breaker may be open (see `circuit-breaker-open` runbook)

6. **Restart Services**
   ```bash
   docker compose restart api
   ```

### Escalation
- If unresolved in 15 minutes, escalate to on-call backend engineer.
- Page backend team for database or storage issues.

---

## latency-high

**Alert**: P95 latency > 5 seconds

### Symptoms
- Slow response times in UI
- SSE streams taking too long to start or lagging
- Sentry Performance dashboard showing high latency transactions

### Causes
1. **Slow LLM responses**: OpenRouter or underlying models (Gemini/Grok) responding slowly.
2. **Complex Qdrant queries**: High `top_k` or complex filtering causing slow vector searches.
3. **Resource contention**: High CPU/Memory usage on the API server.
4. **Database bottlenecks**: Slow queries on PostgreSQL.

### Resolution Steps
1. **Identify slow transactions in Sentry**
   - Sentry → Performance → Identify the slow endpoints (usually `/api/compare/` or `/api/stream/search`).

2. **Check Resource Usage**
   ```bash
   docker stats
   top
   ```

3. **Check Qdrant metrics**
   - Check if indexing is happening in background: `curl http://localhost:6333/collections`

4. **Review LLM Latency**
   - Check OpenRouter dashboard if accessible.
   - Consider switching to faster models in `backend/app/config.py` if necessary.

5. **Clear Semantic Cache** (if applicable)
   ```bash
   python main.py cache-clear
   ```

### Escalation
- If P99 latency exceeds 30 seconds for more than 10 minutes, escalate to Lead Architect.

---

## circuit-breaker-open

**Alert**: Circuit breaker `qdrant_breaker`, `llm_breaker`, or `embeddings_breaker` entered OPEN state.

### Symptoms
- Immediate errors without waiting for timeouts (fail-fast)
- Sentry logs showing `CircuitBreakerError`
- Frontend showing "Service Temporarily Unavailable" or "Degraded" status in health check.

### Causes
1. **Target service down**: Qdrant or OpenRouter is offline.
2. **Network instability**: Frequent connection timeouts or DNS issues.
3. **Sustained high error rate**: Service is up but returning errors consistently.

### Resolution Steps
1. **Identify which breaker is open**
   - Check `backend/api/health` output for `qdrant` status.
   - Check logs for `CircuitBreakerError: <breaker_name>`.

2. **Verify target service health**
   - **Qdrant**: `curl http://localhost:6333/healthz`
   - **OpenRouter**: Check https://status.openrouter.ai/

3. **Wait for Auto-Reset**
   - Breakers are configured to reset after 30s-120s. Monitor logs for transitions to `HALF_OPEN`.

4. **Manual Intervention**
   - If a service is stuck in a bad state, restart it:
     ```bash
     docker compose restart qdrant
     ```

### Escalation
- If `qdrant_breaker` remains open for > 5 minutes, page the Database Reliability team.

---

## llm-error-rate

**Alert**: LLM API (OpenRouter) error rate > 10%

### Symptoms
- Q&A or Comparative analysis failing with LLM errors.
- Sentry showing 4xx or 5xx responses from OpenRouter.
- Logs showing "LLM API Error" or "OpenRouter error".

### Causes
1. **API Key Issues**: Invalid, expired, or quota-exhausted `OPENROUTER_API_KEY`.
2. **Model Availability**: Requested model (Gemini 2.5 Flash, Grok 4.1 Fast) is down or overloaded.
3. **Rate Limiting**: Exceeding OpenRouter's rate limits for the current tier.
4. **Invalid Prompts**: Malformed requests causing 400 Bad Request.

### Resolution Steps
1. **Check OpenRouter status**
   - Visit https://status.openrouter.ai/
   - Check OpenRouter Activity dashboard for error patterns.

2. **Verify API Key**
   - Ensure `OPENROUTER_API_KEY` in `backend/.env` is correct.
   - Check balance/usage on OpenRouter.

3. **Check logs for specific LLM errors**
   ```bash
   docker compose logs api | grep -i "llm"
   ```

4. **Temporarily switch models** (if a specific model is failing)
   - Update model names in `backend/app/config.py`.

### Escalation
- If API keys are exhausted, contact the project owner to top up credits.
- If OpenRouter is down globally, update status page for Clarus users.
