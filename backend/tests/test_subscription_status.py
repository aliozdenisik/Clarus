from __future__ import annotations

from fastapi.testclient import TestClient

from app.auth.api_key_validator import get_current_user_flexible
from app.main import app


def _fake_user() -> dict:
    return {"id": "test_sub_user_001", "email": "test@example.com"}


class TestSubscriptionStatusEndpoint:
    def test_subscription_status_returns_tier_and_limit(self) -> None:
        app.dependency_overrides[get_current_user_flexible] = _fake_user
        try:
            client = TestClient(app)
            response = client.get("/api/subscription/status")
            assert response.status_code == 200
            data = response.json()
            assert "tier" in data
            assert "limit" in data
            assert isinstance(data["tier"], str)
            assert isinstance(data["limit"], int)
        finally:
            app.dependency_overrides.pop(get_current_user_flexible, None)
