from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError

from app.main import app


def _make_pydantic_error() -> ValidationError:
    class _M(BaseModel):
        x: int

    try:
        _M(x="not_an_int")  # type: ignore[arg-type]
    except ValidationError as exc:
        return exc
    raise RuntimeError("unreachable")  # pragma: no cover


def _mock_event(event_type: str, external_id: str) -> MagicMock:
    evt = MagicMock()
    evt.TYPE = event_type
    evt.data.customer.external_id = external_id
    return evt


class TestPolarWebhookInvalidSignature:
    def setup_method(self) -> None:
        self.client = TestClient(app)

    def test_invalid_signature_returns_403(self) -> None:
        from polar_sdk.webhooks import WebhookVerificationError  # type: ignore[attr-defined]

        with (
            patch("app.api.webhooks.settings") as mock_settings,
            patch(
                "app.api.webhooks.validate_event",
                side_effect=WebhookVerificationError("bad signature"),
            ),
        ):
            mock_settings.polar_webhook_secret = "test-secret"
            response = self.client.post(
                "/api/webhooks/polar",
                content=b'{"type":"test"}',
                headers={"Content-Type": "application/json"},
            )
        assert response.status_code == 403
        assert response.json()["error"] == "Invalid signature"


class TestPolarWebhookSubscriptionActive:
    def setup_method(self) -> None:
        self.client = TestClient(app)

    def test_subscription_active_calls_set_tier_pro_and_returns_202(self) -> None:
        mock_event = _mock_event("subscription.active", "user_ext_001")
        mock_event.data.product_id = "ebb31859-0ddb-4025-b047-5e7358221400"
        with (
            patch("app.api.webhooks.settings") as mock_settings,
            patch("app.api.webhooks.validate_event", return_value=mock_event),
            patch("app.api.webhooks.set_tier", new_callable=AsyncMock) as mock_set,
        ):
            mock_settings.polar_webhook_secret = "test-secret"
            mock_settings.polar_pro_product_id = "ebb31859-0ddb-4025-b047-5e7358221400"
            mock_settings.polar_starter_product_id = "63ef5ef3-d771-42ae-9742-fe185800d255"
            response = self.client.post(
                "/api/webhooks/polar",
                content=b"{}",
                headers={"Content-Type": "application/json"},
            )
        assert response.status_code == 202
        assert response.json()["status"] == "ok"
        mock_set.assert_called_once()
        args = mock_set.call_args.args
        assert args[1] == "user_ext_001"
        assert args[2] == "pro"


class TestPolarWebhookSubscriptionRevoked:
    def setup_method(self) -> None:
        self.client = TestClient(app)

    def test_subscription_revoked_calls_set_tier_free_and_returns_202(self) -> None:
        mock_event = _mock_event("subscription.revoked", "user_ext_002")
        with (
            patch("app.api.webhooks.settings") as mock_settings,
            patch("app.api.webhooks.validate_event", return_value=mock_event),
            patch("app.api.webhooks.set_tier", new_callable=AsyncMock) as mock_set,
        ):
            mock_settings.polar_webhook_secret = "test-secret"
            response = self.client.post(
                "/api/webhooks/polar",
                content=b"{}",
                headers={"Content-Type": "application/json"},
            )

        assert response.status_code == 202
        assert response.json()["status"] == "ok"
        mock_set.assert_called_once()
        args = mock_set.call_args.args
        assert args[1] == "user_ext_002"
        assert args[2] == "free"


class TestPolarWebhookUnknownEvent:
    def setup_method(self) -> None:
        self.client = TestClient(app)

    def test_unknown_event_type_returns_202_unknown_event(self) -> None:
        with (
            patch("app.api.webhooks.settings") as mock_settings,
            patch(
                "app.api.webhooks.validate_event",
                side_effect=_make_pydantic_error(),
            ),
        ):
            mock_settings.polar_webhook_secret = "test-secret"
            response = self.client.post(
                "/api/webhooks/polar",
                content=b"{}",
                headers={"Content-Type": "application/json"},
            )

        assert response.status_code == 202
        assert response.json()["status"] == "unknown_event"


class TestPolarWebhookIdempotency:
    def setup_method(self) -> None:
        self.client = TestClient(app)

    def test_duplicate_webhook_id_returns_202_already_processed(self) -> None:
        mock_redis = MagicMock()
        mock_redis.set = AsyncMock(return_value=None)
        with patch("app.api.webhooks.redis_manager") as mock_rm:
            mock_rm.client = mock_redis
            response = self.client.post(
                "/api/webhooks/polar",
                content=b"{}",
                headers={
                    "Content-Type": "application/json",
                    "webhook-id": "idempotent-webhook-id-xyz",
                },
            )

        assert response.status_code == 202
        assert response.json()["status"] == "already_processed"
