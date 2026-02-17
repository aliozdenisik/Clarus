# Security Best Practices Report

Date: 2026-02-17
Scope: backend (FastAPI), frontend (Next.js), tracked repository content

## Executive Summary

The repository was audited before public visibility with parallel code scans, secret detection, and best-practice review. High-impact issues were found and fixed in code. One category remains manual: credential rotation for local environment files and any previously leaked credentials outside this commit.

## Critical Findings

### SBP-001 - Secret-like values in tracked documentation (Fixed)
- Severity: Critical
- Impact: Real-looking credential strings in tracked files can be harvested by crawlers and reused in abuse attempts.
- Evidence: `docs/security/SECURITY_AUDIT_2026-02-03.md:35`, `docs/security/SECURITY_AUDIT_2026-02-03.md:36`, `docs/security/SECURITY_AUDIT_2026-02-03.md:37`
- Fix applied: Redacted values in tracked document.

### SBP-002 - Public expensive endpoints lacked IP throttling (Fixed)
- Severity: Critical
- Impact: Anonymous scraping/flooding of metadata and morphology endpoints can cause resource exhaustion.
- Evidence: public endpoint prefixes were not covered by middleware limits before update.
- Fix applied:
  - Added public path throttling buckets in `backend/app/middleware/rate_limit.py:139`
  - Enforced per-minute public limit using `public_rate_limit_per_minute` from `backend/app/config.py:33`
  - Enabled middleware wiring in `backend/app/main.py:200`

## High Findings

### SBP-003 - Production config guardrails were incomplete (Fixed)
- Severity: High
- Impact: Unsafe deployment combinations (wildcard CORS with credentials, localhost in production URLs, disabled rate limit in production) could silently ship.
- Evidence: `backend/app/config.py:96`
- Fix applied:
  - Added runtime validation for dangerous CORS combinations at `backend/app/config.py:98`
  - Added production check for disabled rate limiting at `backend/app/config.py:107`
  - Added localhost/loopback rejection and HTTPS enforcement for Better Auth endpoints at `backend/app/config.py:110` and `backend/app/config.py:123`

### SBP-004 - HSTS was always emitted regardless of context (Fixed)
- Severity: High
- Impact: Always-on HSTS can break non-TLS development/proxy scenarios and creates brittle behavior.
- Evidence: `backend/app/middleware/security_headers.py:65`
- Fix applied: HSTS now only applies in production over HTTPS (`backend/app/middleware/security_headers.py:66`).

### SBP-005 - Session cookie token parsing duplicated and brittle (Fixed)
- Severity: High
- Impact: Inconsistent parsing logic increases auth bypass/edge-case risk.
- Evidence: parsing logic existed in multiple places before this pass.
- Fix applied:
  - Centralized extraction helper in `backend/app/auth/api_key_validator.py:19`
  - Reused helper in `backend/app/auth/api_key_validator.py:199`
  - Reused helper in SSE auth path `backend/app/api/stream.py:73`

### SBP-006 - `window.open` without explicit opener isolation (Fixed)
- Severity: High
- Impact: Reverse-tabnabbing risk from newly opened tabs.
- Evidence:
  - `frontend/components/compare/inline-citation.tsx:35`
  - `frontend/app/[locale]/compare/page.tsx:261`
  - `frontend/app/[locale]/search/page.tsx:290`
- Fix applied: all open calls now use `noopener,noreferrer`.

## Medium Findings

### SBP-007 - SSE query length constraints were implicit (Fixed)
- Severity: Medium
- Impact: Unbounded query strings increase abuse and memory pressure risk.
- Evidence:
  - `backend/app/api/stream.py:91`
  - `backend/app/api/stream.py:280`
- Fix applied: explicit `min_length=1`, `max_length=500` on SSE query parameters.

## Manual Follow-ups (Cannot be safely automated in code)

### SBP-M01 - Rotate local credentials and provider secrets (Manual Required)
- Severity: Critical
- Why manual: requires external provider actions and may impact live integrations.
- Action:
  1. Rotate OpenRouter key
  2. Rotate Google OAuth client secret
  3. Rotate Better Auth secret
  4. Rotate Sentry auth tokens/DSNs if exposed externally

### SBP-M02 - Optional git history rewrite for past leaks (Manual/Explicit Approval)
- Severity: High
- Why manual: destructive history rewrite requires coordinated force push.
- Action: run history rewrite only with explicit team approval, then rotate affected credentials.

## Verification Evidence

- Secret scan: `pre-commit run gitleaks --all-files` -> passed
- Backend lint: `uv run ruff check ...` -> passed
- Backend format: `uv run ruff format --check ...` -> passed
- Backend type check: `uv run pyright ...` -> passed
- Backend tests: `uv run pytest tests/test_health_endpoint.py tests/test_api_locale_integration.py -q` -> 42 passed
- Frontend lint: `npm run lint` -> passed
- Frontend tests: `npm test -- --run __tests__/compare-page.test.tsx __tests__/search-page.test.tsx __tests__/inline-citation.test.tsx` -> 37 passed
- Frontend build: `npm run build` -> passed
- Frontend project-wide typecheck: `npx tsc --noEmit` -> fails on pre-existing i18n test typing issues unrelated to this patch
