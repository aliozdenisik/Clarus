# Known Issues Tracker

**Last Updated:** 2026-01-27

This file tracks known issues, bugs, and technical debt discovered during development.

---

## Open Issues

### Issue #1: Pre-existing Frontend Test Failures (Navigation URL Mismatch)

**Status:** Open
**Priority:** Low
**Discovered:** 2026-01-27
**Location:** `frontend/__tests__/`

**Affected Files:**
- `frontend/__tests__/old-testament.test.tsx`
- `frontend/__tests__/new-testament.test.tsx`
- `frontend/__tests__/apocrypha.test.tsx`

**Description:**
Three browse page tests fail due to navigation URL mismatch. Tests expect `/search?source=ot&book=1` but actual navigation goes to `/bible/1`.

**Error Message:**
```
AssertionError: expected "spy" to be called with arguments: [ '/search?source=ot&book=1' ]
Received: [ '/bible/1' ]
```

**Root Cause:**
The page components were updated to use direct Bible routes (`/bible/{bookNr}`) instead of search routes with query parameters. Tests were not updated to match.

**Fix Required:**
Update test assertions to expect the new URL format:
```typescript
// OLD (incorrect)
expect(mockPush).toHaveBeenCalledWith('/search?source=ot&book=1');

// NEW (correct)
expect(mockPush).toHaveBeenCalledWith('/bible/1');
```

**Files to Modify:**
- `frontend/__tests__/old-testament.test.tsx` line 113
- `frontend/__tests__/new-testament.test.tsx` line 113
- `frontend/__tests__/apocrypha.test.tsx` line 113

---

### Issue #2: Pydantic V2 Deprecation Warnings (Backend)

**Status:** Open
**Priority:** Low
**Discovered:** 2026-01-27
**Location:** `backend/app/`

**Affected Files:**
- `backend/app/config.py:6`
- `backend/app/auth/schemas.py:21`
- `backend/app/schemas/common.py:18`

**Description:**
Pydantic V2 deprecation warnings about class-based `config`. Should migrate to `ConfigDict`.

**Warning Message:**
```
PydanticDeprecatedSince20: Support for class-based `config` is deprecated, 
use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0.
```

**Fix Required:**
```python
# OLD
class Settings(BaseSettings):
    class Config:
        env_file = ".env"

# NEW
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")
```

---

### Issue #3: Python crypt Module Deprecation Warning

**Status:** Open
**Priority:** Low
**Discovered:** 2026-01-27
**Location:** `passlib` dependency

**Description:**
The `passlib` library uses the deprecated `crypt` module which will be removed in Python 3.13.

**Warning Message:**
```
DeprecationWarning: 'crypt' is deprecated and slated for removal in Python 3.13
```

**Fix Required:**
- Update `passlib` to a newer version when available
- Or migrate to `argon2-cffi` or `bcrypt` directly

---

## Resolved Issues

*No resolved issues yet.*

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
