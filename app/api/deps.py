import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.user import User
from app.services import AuthService, PortfolioService, RiskService

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


PortfolioServiceDep = Annotated[PortfolioService, Depends(get_portfolio_service)]
RiskServiceDep = Annotated[RiskService, Depends(get_risk_service)]
