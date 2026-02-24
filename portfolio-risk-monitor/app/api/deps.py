from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.services import PortfolioService, RiskService

DBSession = Annotated[AsyncSession, Depends(get_session)]


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
