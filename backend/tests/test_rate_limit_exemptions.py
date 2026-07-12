from unittest.mock import AsyncMock

import pytest

from app.api.auth import check_rate_limit
from app.config import settings


def test_rate_limit_exempt_emails_are_normalized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "rate_limit_exempt_emails", " First@Example.com,second@example.com , ")

    assert settings.rate_limit_exempt_emails_set == {"first@example.com", "second@example.com"}


@pytest.mark.asyncio
async def test_exempt_user_bypasses_rate_limit_without_database_access(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(settings, "rate_limit_exempt_emails", "approved@example.com")
    db = AsyncMock()

    await check_rate_limit(
        {"id": "approved-user", "email": " Approved@Example.com "},
        db,
    )

    db.execute.assert_not_awaited()
    db.commit.assert_not_awaited()
