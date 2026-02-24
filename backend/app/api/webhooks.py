"""Polar.sh webhook handler for Clarus backend.

Processes subscription lifecycle events (active/revoked) and updates
user tiers in Redis via set_tier().
"""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from polar_sdk.webhooks import WebhookVerificationError, validate_event  # type: ignore[attr-defined]
from pydantic import ValidationError

from app.config import settings
from app.polar_tier import set_tier
from app.redis_client import redis_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/polar",
    responses={
        202: {"description": "Accepted — event processed, duplicate, or unknown"},
        403: {"description": "Forbidden — invalid signature or webhook not configured"},
    },
)
async def handle_polar_webhook(request: Request) -> JSONResponse:
    """Handle incoming Polar.sh webhook events.

    Flow:
    1. Read raw body and headers.
    2. Verify HMAC signature with validate_event().
    3. Idempotency check via Redis SETNX (24h TTL) — AFTER signature verification.
    4. Route subscription.active / subscription.revoked to tier management.

    Returns 202 Accepted for all responses (Polar canonical response).
    Returns 403 for invalid webhook signatures.
    """
    body = await request.body()
    headers = dict(request.headers)
    webhook_id = headers.get("webhook-id")

    # Guard: reject immediately if webhook secret is not configured
    if not settings.polar_webhook_secret:  # type: ignore[attr-defined]
        logger.warning("Polar webhook secret not configured, rejecting request")
        return JSONResponse(status_code=403, content={"error": "Webhook not configured"})

    # Signature verification + event parsing (raises on failure)
    try:
        event = validate_event(
            body=body,
            headers=headers,
            secret=settings.polar_webhook_secret,  # type: ignore[attr-defined]
        )
    except WebhookVerificationError:
        logger.warning(
            "Invalid Polar webhook signature",
            extra={"webhook_id": webhook_id},
        )
        return JSONResponse(status_code=403, content={"error": "Invalid signature"})
    except ValidationError:
        logger.info(
            "Unknown Polar webhook event type, ignoring",
            extra={"webhook_id": webhook_id},
        )
        return JSONResponse(status_code=202, content={"status": "unknown_event"})

    # Idempotency: skip webhooks already processed (checked AFTER signature verification)
    # Wrapped in try/except for fail-open: Redis errors must not block webhook processing
    if webhook_id and redis_manager.client:
        try:
            idempotency_key = f"polar:webhook:{webhook_id}"
            was_set = await redis_manager.client.set(idempotency_key, b"1", nx=True, ex=86400)
            if was_set is None:
                logger.info(
                    "Duplicate Polar webhook skipped",
                    extra={"webhook_id": webhook_id},
                )
                return JSONResponse(status_code=202, content={"status": "already_processed"})
        except Exception:
            logger.warning(
                "Redis idempotency check failed, proceeding with webhook processing",
                extra={"webhook_id": webhook_id},
                exc_info=True,
            )

    event_type: str = event.TYPE  # type: ignore[union-attr]
    logger.info(
        "Polar webhook received",
        extra={"event_type": event_type, "webhook_id": webhook_id},
    )

    if event_type == "subscription.active":
        external_id: str | None = event.data.customer.external_id  # type: ignore[union-attr]
        if external_id:
            product_id = getattr(event.data, "product_id", None)  # type: ignore[union-attr]
            if product_id == settings.polar_pro_product_id:  # type: ignore[attr-defined]
                tier = "pro"
            elif product_id == settings.polar_starter_product_id:  # type: ignore[attr-defined]
                tier = "starter"
            else:
                logger.warning(
                    "Unknown product_id in subscription.active — skipping tier update",
                    extra={"product_id": product_id, "external_id": external_id, "webhook_id": webhook_id},
                )
                return JSONResponse(status_code=202, content={"status": "unknown_product"})
            await set_tier(redis_manager.client, external_id, tier)
            logger.info(
                "User subscription activated",
                extra={"external_id": external_id, "tier": tier, "webhook_id": webhook_id},
            )
    elif event_type == "subscription.revoked":
        external_id = event.data.customer.external_id  # type: ignore[union-attr]
        if external_id:
            await set_tier(redis_manager.client, external_id, "free")
            logger.info(
                "User downgraded to free tier",
                extra={"external_id": external_id, "webhook_id": webhook_id},
            )
    else:
        logger.info(
            "Unhandled Polar webhook event",
            extra={"event_type": event_type, "webhook_id": webhook_id},
        )

    return JSONResponse(status_code=202, content={"status": "ok"})
