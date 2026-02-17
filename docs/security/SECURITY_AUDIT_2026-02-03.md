# Clarus Security Audit Report

**Date:** 2026-02-03  
**Auditor:** Automated Security Scan  
**Status:** Pre-Production Assessment  
**Severity:** CRITICAL - Do not deploy to production without remediation

---

## Executive Summary

| Severity | Count | Status |
|----------|-------|--------|
| **CRITICAL** | 7 | Immediate action required |
| **HIGH** | 10 | Fix within 1 week |
| **MEDIUM** | 9 | Fix within sprint |
| **LOW** | 4 | Monitor and fix |

**Recommendation:** This application should NOT be deployed to production until all CRITICAL and HIGH severity vulnerabilities are addressed.

---

## CRITICAL Vulnerabilities

### CVE-LOCAL-001: Exposed API Keys in Repository

**Severity:** CRITICAL  
**CVSS Score:** 9.8  
**File:** `/backend/.env`  
**Lines:** 3, 13-14, 35

**Description:**
Real API keys and secrets are present in the working directory:
```
OPENROUTER_API_KEY=sk-or-v1-REDACTED_ROTATE_REQUIRED
GOOGLE_CLIENT_SECRET=REDACTED_ROTATE_REQUIRED
JWT_SECRET_KEY=REDACTED_ROTATE_REQUIRED
```

**Impact:**
- Attackers can impersonate the application
- API calls can be made at the organization's expense
- Full authentication bypass via forged JWT tokens
- Google OAuth account takeover

**Remediation:**
1. Immediately rotate all exposed credentials:
   - OpenRouter API key
   - Google OAuth client secret
   - JWT secret key
2. Remove `.env` from git history:
   ```bash
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch backend/.env' \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. Use secrets management (AWS Secrets Manager, HashiCorp Vault)

---

### CVE-LOCAL-002: Hardcoded Default JWT Secret

**Severity:** CRITICAL  
**CVSS Score:** 9.1  
**File:** `/backend/app/config.py`  
**Line:** 14

**Description:**
```python
jwt_secret_key: str = "your-secret-key-change-in-production"
```

If `.env` is not configured, the application uses a publicly known default secret.

**Impact:**
- Complete authentication bypass
- Any attacker can forge valid JWT tokens
- Unauthorized access to all protected endpoints

**Remediation:**
```python
import os

jwt_secret_key: str = os.environ.get("JWT_SECRET_KEY")
if not jwt_secret_key or jwt_secret_key == "your-secret-key-change-in-production":
    raise RuntimeError("JWT_SECRET_KEY must be set to a secure value")
```

---

### CVE-LOCAL-003: JWT Token Exposed in Query Parameters

**Severity:** CRITICAL  
**CVSS Score:** 8.5  
**File:** `/backend/app/api/stream.py`  
**Lines:** 66-69

**Description:**
```python
token: str = Query(
    ...,
    description="JWT access token (required for SSE - EventSource can't send headers)",
)
```

**Impact:**
Tokens are logged in:
- Server access logs
- Browser history
- Proxy/CDN logs
- Referrer headers to external sites
- Network monitoring tools

**Remediation:**
- Use POST request with token in body
- Or implement WebSocket with proper authentication
- Or use custom EventSource with Authorization header

---

### CVE-LOCAL-004: SQL Injection via String Interpolation

**Severity:** HIGH (Currently mitigated by integer conversion)  
**CVSS Score:** 7.5  
**Files:**
- `/backend/src/quran_morphology.py` (Lines 567-571)
- `/backend/src/bible_morphology.py` (Lines 997-1001)

**Description:**
```python
placeholders = ",".join(str(aid) for aid in ayah_ids)
batch_words_result = await session.execute(
    sa_text(
        f"SELECT DISTINCT ayah_id, token_clean FROM qm_words "
        f"WHERE ayah_id IN ({placeholders}) AND root = :root "
    ),
    {"root": root},
)
```

**Impact:**
Anti-pattern that bypasses SQLAlchemy's parameterization. If data source changes to include user input, SQL injection becomes possible.

**Remediation:**
```python
from sqlalchemy import select
from sqlalchemy.orm import aliased

# Use SQLAlchemy's in_() operator
stmt = (
    select(QmWords.ayah_id, QmWords.token_clean)
    .where(QmWords.ayah_id.in_(ayah_ids))
    .where(QmWords.root == root)
    .where(QmWords.token_clean.isnot(None))
    .distinct()
)
result = await session.execute(stmt)
```

---

### CVE-LOCAL-005: Unauthenticated API Endpoints

**Severity:** CRITICAL  
**CVSS Score:** 8.0  
**Files:**
- `/backend/app/api/keyword_search.py` (Lines 35-152)
- `/backend/app/api/metadata.py` (Lines 84-251)

**Description:**
Multiple endpoints accessible without authentication:
```python
@router.post("/", response_model=KeywordSearchResponse)
async def search_keyword(request: KeywordSearchRequest):  # NO AUTH
    ...

@router.get("/roots", response_model=RootListResponse)
async def list_roots(...):  # NO AUTH
    ...
```

**Impact:**
- Rate limiting bypass (no user_id to track)
- Data enumeration without authorization
- No audit trail

**Remediation:**
```python
from app.api.auth import get_current_user, check_rate_limit

@router.post("/", response_model=KeywordSearchResponse)
async def search_keyword(
    request: KeywordSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_rate_limit(current_user, db)
    ...
```

---

### CVE-LOCAL-006: Debug Mode Enabled by Default

**Severity:** CRITICAL  
**CVSS Score:** 7.5  
**File:** `/backend/app/config.py`  
**Line:** 38

**Description:**
```python
debug: bool = True
```

Debug mode is hardcoded to `True` regardless of environment.

**Impact:**
- Stack traces exposed in error responses
- Internal file paths revealed
- Database structure exposed
- Third-party service details leaked

**Remediation:**
```python
debug: bool = False  # Default to False
app_env: str = "development"

# Add validation in startup
if settings.debug and settings.is_production:
    raise RuntimeError("Debug mode cannot be enabled in production")
```

---

### CVE-LOCAL-007: CORS Misconfiguration

**Severity:** HIGH  
**CVSS Score:** 7.0  
**File:** `/backend/app/main.py`  
**Lines:** 170-171

**Description:**
```python
allow_methods=["*"],
allow_headers=["*"],
```

**Impact:**
- CSRF attacks possible
- Unauthorized state-changing operations (DELETE, PATCH)

**Remediation:**
```python
allow_methods=["GET", "POST", "OPTIONS"],
allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
```

---

## HIGH Severity Vulnerabilities

### CVE-LOCAL-008: JWT Tokens Stored in localStorage

**File:** `/frontend/lib/auth/auth-context.tsx`  
**Lines:** 114-115, 138-139

**Description:**
```typescript
localStorage.setItem("access_token", data.access_token);
localStorage.setItem("refresh_token", data.refresh_token);
```

**Impact:** XSS vulnerability allows token theft.

**Remediation:** Migrate to HttpOnly cookies with Secure and SameSite flags.

---

### CVE-LOCAL-009: Weak XSS Sanitization

**File:** `/backend/app/schemas/common.py`  
**Lines:** 172-179

**Description:**
```python
xss_patterns = ["<script", "</script", "javascript:", "onerror=", "onclick="]
for pattern in xss_patterns:
    sanitized = sanitized.replace(pattern, "")  # Case-sensitive, incomplete
```

**Impact:** XSS bypass via case variations, encoding, or missing patterns.

**Remediation:** Use `html.escape()` for HTML context.

---

### CVE-LOCAL-010: SSRF in OAuth Redirect URI

**File:** `/backend/app/api/auth.py`  
**Line:** 190

**Description:**
```python
"redirect_uri": auth_data.redirect_uri or settings.google_redirect_uri,
```

**Impact:** Open redirect attacks, OAuth bypass.

**Remediation:** Whitelist allowed redirect URIs.

---

### CVE-LOCAL-011: Verbose Error Messages

**Files:**
- `/backend/app/api/stream.py` (Lines 59, 165, 217)
- `/backend/app/middleware/error_handler.py` (Line 142)

**Description:**
```python
yield f"data: {json.dumps({'error': str(e)})}\n\n"
```

**Impact:** Information disclosure about internal systems.

**Remediation:** Return generic error messages in production.

---

### CVE-LOCAL-012: Missing Security Headers

**File:** `/backend/app/main.py`

**Missing Headers:**
- `Strict-Transport-Security`
- `X-Content-Type-Options`
- `X-Frame-Options`
- `Content-Security-Policy`

**Remediation:** Add security headers middleware.

---

### CVE-LOCAL-013: No CSRF Protection

**File:** `/backend/app/main.py`

**Impact:** Cross-site request forgery on state-changing operations.

**Remediation:** Implement CSRF tokens or use SameSite cookies.

---

### CVE-LOCAL-014: No Rate Limiting on Auth Endpoints

**File:** `/backend/app/api/auth.py`  
**Lines:** 118-178

**Impact:** Brute force attacks on login, credential stuffing.

**Remediation:** Add IP-based rate limiting (5 attempts/minute).

---

### CVE-LOCAL-015: Weak Admin Authorization

**File:** `/backend/app/api/admin.py`  
**Lines:** 14-20

**Description:**
```python
ADMIN_EMAILS = ["admin@hollysearch.com", "test@example.com"]
```

**Impact:** Hardcoded admin list, test account in production.

**Remediation:** Implement RBAC with database-backed roles.

---

### CVE-LOCAL-016: No Refresh Token Rotation

**File:** `/backend/app/api/auth.py`  
**Lines:** 260-286

**Impact:** Compromised refresh token grants indefinite access.

**Remediation:** Implement token rotation with reuse detection.

---

### CVE-LOCAL-017: Unvalidated Query Parameters

**File:** `/backend/app/api/stream.py`  
**Lines:** 103-110

**Description:**
```python
source: str = Query(default="quran")  # NOT VALIDATED
```

**Remediation:** Use Pydantic Enum for validation.

---

## MEDIUM Severity Vulnerabilities

### CVE-LOCAL-018: No Password Complexity Validation
**File:** `/backend/app/auth/schemas.py:8-13`

### CVE-LOCAL-019: No Account Lockout
**File:** `/backend/app/api/auth.py:150-178`

### CVE-LOCAL-020: No HTTPS Enforcement
**File:** `/backend/app/config.py:21`

### CVE-LOCAL-021: Plaintext Refresh Tokens in Database
**File:** `/backend/app/models.py:33`

### CVE-LOCAL-022: Hardcoded Database Credentials
**File:** `/backend/app/api/keyword_search.py:30`

### CVE-LOCAL-023: No Token Expiration Check in Frontend
**File:** `/frontend/lib/auth/auth-context.tsx:36-56`

### CVE-LOCAL-024: No Audit Logging
**File:** `/backend/app/api/auth.py`

### CVE-LOCAL-025: Missing Cookie Security Flags
**File:** `/backend/app/api/auth.py`

### CVE-LOCAL-026: Default PostgreSQL Password
**File:** `/docker-compose.yml:11`

---

## LOW Severity Vulnerabilities

### CVE-LOCAL-027: Path Traversal Anti-Pattern
**File:** `/backend/app/api/metadata.py:10-11`

### CVE-LOCAL-028: Sensitive Data in Logs
**File:** `/backend/app/api/search.py:118`

### CVE-LOCAL-029: Test Credentials File in Repo
**File:** `/test-credentials.json`

### CVE-LOCAL-030: No Rate Limit on OAuth Endpoint
**File:** `/backend/app/api/auth.py:181`

---

## Remediation Priority

### Immediate (Today)
1. Rotate all exposed credentials
2. Remove `.env` from git history
3. Disable debug mode

### Urgent (This Week)
4. Add authentication to all endpoints
5. Remove JWT from query parameters
6. Add security headers
7. Fix CORS configuration
8. Fix XSS sanitization

### Important (This Sprint)
9. Migrate to HttpOnly cookies
10. Fix SQL injection anti-pattern
11. Add CSRF protection
12. Add auth rate limiting
13. Add password complexity validation
14. Add account lockout

### Scheduled (Next Sprint)
15. Implement refresh token rotation
16. Add comprehensive audit logging
17. Implement RBAC
18. Hash refresh tokens

---

## Testing Recommendations

After remediation, run:

```bash
# OWASP ZAP scan
docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:8000

# SQL injection testing
sqlmap -u "http://localhost:8000/api/search/keyword" --data='{"query":"test"}' --level=5

# Nuclei vulnerability scan
nuclei -u http://localhost:8000 -t cves/ -t vulnerabilities/
```

---

## Compliance Notes

This audit identified issues relevant to:
- **OWASP Top 10 2021:** A01 (Broken Access Control), A02 (Cryptographic Failures), A03 (Injection), A05 (Security Misconfiguration), A07 (Identification and Authentication Failures)
- **CWE:** CWE-798 (Hardcoded Credentials), CWE-89 (SQL Injection), CWE-79 (XSS), CWE-352 (CSRF)

---

*Report generated: 2026-02-03T13:16:29+03:00*
