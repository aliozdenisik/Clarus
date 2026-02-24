import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.api_key_validator import get_current_user_flexible
from app.config import settings
from app.polar_tier import get_tier
from app.redis_client import redis_manager

logger = logging.getLogger(__name__)
router = APIRouter()


class SubscriptionStatusResponse(BaseModel):
    """Response model for subscription status endpoint."""

    tier: str
    limit: int


@router.get(
    "/status",
    response_model=SubscriptionStatusResponse,
    openapi_extra={"security": [{"SessionCookieAuth": []}, {"ApiKeyAuth": []}]},
)
async def get_subscription_status(user: dict = Depends(get_current_user_flexible)):
    """Return the user's subscription tier and rate limit."""
    user_id = user["id"]
    tier = await get_tier(redis_manager.client, user_id)
    tier_limits = getattr(settings, "tier_rate_limits", {"free": 50, "starter": 200, "pro": 500})
    limit = tier_limits.get(tier, settings.rate_limit_per_day)
    return SubscriptionStatusResponse(tier=tier, limit=limit)
