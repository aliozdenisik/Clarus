# Decisions — Better Auth Integration

## 2026-02-06T14:09 Architecture
- Better Auth runs on Next.js (port 3000) — TypeScript only, cannot run on Python
- FastAPI validates JWTs via JWKS endpoint (RS256/ES256 public keys)
- Better Auth creates 4 core tables: user, session, account, verification
- Clarus-specific data goes to `user_stats` table (query_count_today, api_key, etc.)
- Old `users` table renamed to `users_legacy` (not dropped)
- Password hash: Configure Better Auth to use bcrypt (matching current system)
- CLI auth: API key in `X-API-Key` header, stored as SHA256 hash in user_stats

## Hybrid Auth Architecture (Better Auth + FastAPI JWKS)
- **Date:** 2026-02-06
- **Context:** Integrating Better Auth (TypeScript) with Python FastAPI backend.
- **Decision:** Use Next.js as Auth Server (Better Auth) and FastAPI as Resource Server. FastAPI validates tokens via JWKS endpoint exposed by Next.js.
- **Rationale:** Better Auth does not run on Python. This hybrid approach uses standard OIDC patterns and avoids rewriting auth logic in Python or using a separate auth service container.
- **Status:** Accepted
