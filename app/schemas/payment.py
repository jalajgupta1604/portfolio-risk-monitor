from enum import Enum

from pydantic import BaseModel


class SubscriptionTier(str, Enum):
    FREE = "free"
    PAID = "paid"
    PREMIUM = "premium"


TIER_ORDER: dict[str, int] = {"free": 0, "paid": 1, "premium": 2}


class CreateCheckoutRequest(BaseModel):
    tier: str


class CreateCheckoutResponse(BaseModel):
    subscription_id: str
    short_url: str


class SubscriptionStatusResponse(BaseModel):
    tier: str
    expires_at: str | None
    active: bool
