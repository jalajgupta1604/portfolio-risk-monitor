"""Razorpay subscription management service."""

import hashlib
import hmac
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.schemas.payment import SubscriptionTier

logger = logging.getLogger(__name__)

RAZORPAY_BASE = "https://api.razorpay.com/v1"


class PaymentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_subscription(self, user: User, tier: str) -> dict:
        """Create a Razorpay subscription and return subscription_id + short_url."""
        plan_id = (
            settings.RAZORPAY_PLAN_ID_PAID
            if tier == SubscriptionTier.PAID
            else settings.RAZORPAY_PLAN_ID_PREMIUM
        )
        if not plan_id:
            raise ValueError(f"No Razorpay plan configured for tier: {tier}")

        payload = {
            "plan_id": plan_id,
            "total_count": 12,
            "quantity": 1,
            "notes": {"user_id": str(user.id), "email": user.email},
        }

        if user.razorpay_customer_id:
            payload["customer_id"] = user.razorpay_customer_id

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{RAZORPAY_BASE}/subscriptions",
                json=payload,
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET),
            )
            resp.raise_for_status()
            data = resp.json()

        user.razorpay_subscription_id = data["id"]
        self.session.add(user)
        await self.session.commit()

        return {"subscription_id": data["id"], "short_url": data.get("short_url", "")}

    async def handle_webhook(self, body: bytes, signature: str) -> None:
        """Verify and process Razorpay webhook events."""
        expected = hmac.new(
            settings.RAZORPAY_WEBHOOK_SECRET.encode(), body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise ValueError("Invalid webhook signature")

        import json

        payload = json.loads(body)
        event = payload.get("event", "")
        entity = payload.get("payload", {}).get("subscription", {}).get("entity", {})

        sub_id = entity.get("id")
        if not sub_id:
            return

        from sqlalchemy import select

        stmt = select(User).where(User.razorpay_subscription_id == sub_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            logger.warning("No user found for subscription %s", sub_id)
            return

        if event in ("subscription.activated", "subscription.charged"):
            plan_id = entity.get("plan_id", "")
            if plan_id == settings.RAZORPAY_PLAN_ID_PREMIUM:
                user.subscription_tier = SubscriptionTier.PREMIUM
            else:
                user.subscription_tier = SubscriptionTier.PAID

            end_at = entity.get("current_end")
            if end_at:
                user.subscription_expires_at = datetime.fromtimestamp(end_at, tz=timezone.utc)

            if not user.razorpay_customer_id:
                user.razorpay_customer_id = entity.get("customer_id")

        elif event in ("subscription.cancelled", "subscription.completed"):
            user.subscription_tier = SubscriptionTier.FREE
            user.subscription_expires_at = None

        self.session.add(user)
        await self.session.commit()
        logger.info("Webhook %s processed for user %s", event, user.email)

    def get_status(self, user: User) -> dict:
        """Return current subscription status."""
        active = user.subscription_tier != SubscriptionTier.FREE
        if active and user.subscription_expires_at:
            active = user.subscription_expires_at > datetime.now(timezone.utc)
        return {
            "tier": user.subscription_tier,
            "expires_at": user.subscription_expires_at.isoformat() if user.subscription_expires_at else None,
            "active": active,
        }
