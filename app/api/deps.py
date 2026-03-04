import uuid
from collections.abc import AsyncGenerator, Callable
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.user import User
from app.schemas.payment import TIER_ORDER
from app.services import AuthService, BrokerService, PortfolioService, RiskService
from app.services.payment_service import PaymentService

DBSession = Annotated[AsyncSession, Depends(get_session)]

security = HTTPBearer()


async def get_auth_service(session: DBSession) -> AsyncGenerator[AuthService, None]:
    yield AuthService(session)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: DBSession,
) -> User:
    user_id = AuthService.verify_token(credentials.credentials)
    auth = AuthService(session)
    user = await auth.get_user_by_id(uuid.UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_portfolio_service(
    session: DBSession,
) -> AsyncGenerator[PortfolioService, None]:
    yield PortfolioService(session)


async def get_risk_service(
    session: DBSession,
) -> AsyncGenerator[RiskService, None]:
    yield RiskService(session)


async def get_broker_service(
    session: DBSession,
) -> AsyncGenerator[BrokerService, None]:
    yield BrokerService(session)


async def get_payment_service(
    session: DBSession,
) -> AsyncGenerator[PaymentService, None]:
    yield PaymentService(session)


PortfolioServiceDep = Annotated[PortfolioService, Depends(get_portfolio_service)]
RiskServiceDep = Annotated[RiskService, Depends(get_risk_service)]
BrokerServiceDep = Annotated[BrokerService, Depends(get_broker_service)]
PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]


def require_tier(min_tier: str) -> Callable:
    """Dependency factory that enforces a minimum subscription tier."""

    async def _check(current_user: CurrentUser) -> User:
        user_tier = getattr(current_user, "subscription_tier", "free") or "free"
        user_order = TIER_ORDER.get(user_tier, 0)
        min_order = TIER_ORDER.get(min_tier, 0)

        if user_order < min_order:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires '{min_tier}' tier or above. Current tier: '{user_tier}'.",
            )

        # Check expiry
        expires = getattr(current_user, "subscription_expires_at", None)
        if expires and expires < datetime.now(timezone.utc) and user_tier != "free":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your subscription has expired.",
            )

        return current_user

    return _check
