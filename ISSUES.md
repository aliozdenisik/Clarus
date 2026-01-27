# Known Issues Tracker

**Last Updated:** 2026-01-27

This file tracks known issues, bugs, and technical debt discovered during development.

---

## Open Issues

### Issue #1: Pre-existing Frontend Test Failures (Navigation URL Mismatch)

**Status:** ✅ Resolved
**Priority:** Low
**Discovered:** 2026-01-27
**Resolved:** 2026-01-27
**Location:** `frontend/__tests__/`

**Affected Files:**
- `frontend/__tests__/old-testament.test.tsx`
- `frontend/__tests__/new-testament.test.tsx`
- `frontend/__tests__/apocrypha.test.tsx`

**Description:**
Three browse page tests fail due to navigation URL mismatch. Tests expect `/search?source=ot&book=1` but actual navigation goes to `/bible/1`.

**Resolution:**
Updated test assertions to expect the new URL format `/bible/1` instead of `/search?source=ot&book=1`. All 167 tests now pass.

---

### Issue #2: Pydantic V2 Deprecation Warnings (Backend)

**Status:** ✅ Resolved
**Priority:** Low
**Discovered:** 2026-01-27
**Resolved:** 2026-01-27
**Location:** `backend/app/`

**Affected Files:**
- `backend/app/config.py`
- `backend/app/auth/schemas.py`
- `backend/app/schemas/common.py`

**Description:**
Pydantic V2 deprecation warnings about class-based `config`. Migrated to `ConfigDict`.

**Resolution:**
Migrated all 3 files from `class Config` to `model_config = ConfigDict(...)`. No more Pydantic deprecation warnings.

---

### Issue #3: Python crypt Module Deprecation Warning

**Status:** ✅ Resolved
**Priority:** Low
**Discovered:** 2026-01-27
**Resolved:** 2026-01-27
**Location:** `backend/app/auth/__init__.py`

**Description:**
The `passlib` library uses the deprecated `crypt` module which will be removed in Python 3.13.

**Resolution:**
Migrated from passlib to bcrypt directly. Removed passlib dependency, using bcrypt>=4.0.0 instead. Existing password hashes remain compatible (both use $2b$ format).

---

## Resolved Issues

### Issue #1: Pre-existing Frontend Test Failures (Navigation URL Mismatch)
**Resolved:** 2026-01-27
**Fix:** Updated test assertions from `/search?source=ot&book=1` to `/bible/1` in 3 test files.

### Issue #2: Pydantic V2 Deprecation Warnings (Backend)
**Resolved:** 2026-01-27
**Fix:** Migrated from `class Config` to `model_config = ConfigDict(...)` in 3 backend files.

### Issue #3: Python crypt Module Deprecation Warning
**Resolved:** 2026-01-27
**Fix:** Migrated from passlib to bcrypt directly in `backend/app/auth/__init__.py`.

---

## How to Add Issues

When discovering a new issue, add it using this template:

```markdown
### Issue #N: [Brief Title]

**Status:** Open | In Progress | Resolved
**Priority:** Critical | High | Medium | Low
**Discovered:** YYYY-MM-DD
**Location:** [file path or module]

**Description:**
[Detailed description of the issue]

**Error Message:** (if applicable)
```
[error output]
```

**Root Cause:**
[Analysis of why this happens]

**Fix Required:**
[Steps or code changes needed to fix]
```
