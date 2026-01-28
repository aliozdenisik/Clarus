# Test Preparation for Playwright E2E Tests

## Status: Ready for Testing

### Services Status
- ✅ Docker containers (Qdrant + PostgreSQL): Running
- ✅ Backend API (port 8000): Running
- ⏳ Frontend (port 3000): Will be started by Playwright config
- ✅ Playwright: Installed

### Test Environment Setup

**Backend URL:** http://localhost:8000
**Frontend URL:** http://localhost:3000
**Test File:** `/home/freyja/qdrant/frontend/e2e/compare.spec.ts`

### Test User Credentials

Create test user with:
```bash
cd /home/freyja/qdrant/backend
python -c "
import asyncio
from sqlalchemy import create_engine
from app.models import User
from app.db import get_db_url

async def create_test_user():
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    engine = create_async_engine(get_db_url())
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if user exists
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.email == 'browser-test@example.com')
        )
        user = result.scalar_one_or_none()

        if not user:
            from app.api.auth import get_password_hash
            user = User(
                email='browser-test@example.com',
                name='Browser Test User',
                hashed_password=get_password_hash('test123')
            )
            session.add(user)
            await session.commit()
            print('✅ Test user created')
        else:
            print('✅ Test user already exists')

asyncio.run(create_test_user())
"
```

**Test Credentials:**
- Email: `browser-test@example.com`
- Password: `test123`

### Test Execution Commands

**Option 1: Headless (CI mode)**
```bash
cd /home/freyja/qdrant/frontend
npm run test:e2e
```

**Option 2: Headed (see browser)**
```bash
cd /home/freyja/qdrant/frontend
npm run test:e2e:headed
```

**Option 3: Interactive UI**
```bash
cd /home/freyja/qdrant/frontend
npm run test:e2e:ui
```

### Test Coverage

The E2E test suite (`e2e/compare.spec.ts`) covers:

1. ✅ **Authentication Flow** - Login with test credentials
2. ✅ **Navigation** - Navigate to compare page
3. ✅ **Query Submission** - Submit "patience" topic
4. ✅ **Issue #1 Fix Verification** - 5 paragraphs displayed
5. ✅ **Issue #2 Fix Verification** - Statistics show non-zero values
6. ✅ **Verse Cards** - 80 verse cards rendered
7. ✅ **Paragraph Expansion** - Toggle expand/collapse
8. ✅ **Filter Tabs** - Test source filtering (All/Quran/OT/NT/Apocrypha)
9. ✅ **Citation Clicks** - Inline citations open verse pages
10. ✅ **Regression Test** - /stream/search still works

### Expected Test Results

**PASS Criteria:**
- All 5 paragraph titles visible: "Eski Ahit", "Yeni Ahit", "Apokrifa", "Kuran-ı Kerim", "Karşılaştırmalı Değerlendirme"
- Stats show: 80 verses, 5+ citations, >0s latency, >50% confidence
- 80+ verse cards rendered
- Filters change verse count correctly
- Citations are clickable

**Test Duration:** ~90-120 seconds (includes 60-80s for multi-agent analysis)

### Troubleshooting

**If tests fail:**

1. **Check backend logs:**
```bash
tail -f /tmp/backend.log
```

2. **Check frontend console:**
Browser DevTools → Console (if using headed mode)

3. **Verify test user exists:**
```bash
cd /home/freyja/qdrant/backend
python -c "
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import User
from app.db import get_db_url

async def check_user():
    engine = create_async_engine(get_db_url())
    async_session = sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.email == 'browser-test@example.com')
        )
        user = result.scalar_one_or_none()
        if user:
            print(f'✅ User found: {user.email}')
        else:
            print('❌ User not found')

asyncio.run(check_user())
"
```

4. **Manual test:**
- Open http://localhost:3000 in browser
- Login with test credentials
- Navigate to /compare
- Submit query and verify results

### Success Indicators

After tests pass, you should see:
- ✅ All tests passed (green checkmarks)
- ✅ Screenshot saved: `test-results/compare-success.png`
- ✅ HTML report generated: `playwright-report/index.html`

### Next Steps After Tests Pass

1. Review test report: `npx playwright show-report`
2. Check screenshots in `test-results/`
3. Update E2E-COMPARE-TEST-REPORT.md with new status
4. Proceed to deployment

---

**Prepared by:** Claude Code
**Date:** 2026-01-28
**Ready for:** Subagent execution
