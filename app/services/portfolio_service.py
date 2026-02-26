import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Portfolio
from app.repositories import PortfolioRepository, PriceHistoryRepository
from app.schemas.portfolio import (
    BulkPriceUpload,
    HoldingCreate,
    HoldingResponse,
    PortfolioCreate,
    PortfolioResponse,
    PortfolioSummary,
    PortfolioUpdate,
)


class PortfolioService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = PortfolioRepository(session)
        self.price_repo = PriceHistoryRepository(session)

    async def create_portfolio(
        self, data: PortfolioCreate, user_id: uuid.UUID | None = None
    ) -> PortfolioResponse:
        portfolio = await self.repo.create(
            name=data.name, description=data.description, user_id=user_id
        )

        for h in data.holdings:
            await self.repo.add_holding(
                portfolio_id=portfolio.id,
                symbol=h.symbol,
                quantity=h.quantity,
                avg_buy_price=h.avg_buy_price,
                current_price=h.current_price,
            )

        portfolio = await self._get_or_404(portfolio.id, user_id)
        return self._to_response(portfolio)

    async def get_portfolio(
        self, portfolio_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> PortfolioResponse:
        portfolio = await self._get_or_404(portfolio_id, user_id)
        return self._to_response(portfolio)

    async def list_portfolios(
        self, user_id: uuid.UUID | None = None
    ) -> list[PortfolioSummary]:
        portfolios = await self.repo.list_all(user_id=user_id)
        return [self._to_summary(p) for p in portfolios]

    async def update_portfolio(
        self, portfolio_id: uuid.UUID, data: PortfolioUpdate, user_id: uuid.UUID | None = None
    ) -> PortfolioResponse:
        portfolio = await self._get_or_404(portfolio_id, user_id)
        portfolio = await self.repo.update(portfolio, name=data.name, description=data.description)
        return self._to_response(portfolio)

    async def delete_portfolio(
        self, portfolio_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> None:
        await self._get_or_404(portfolio_id, user_id)
        await self.repo.delete(portfolio_id)

    async def add_holding(
        self, portfolio_id: uuid.UUID, data: HoldingCreate, user_id: uuid.UUID | None = None
    ) -> HoldingResponse:
        await self._get_or_404(portfolio_id, user_id)
        holding = await self.repo.add_holding(
            portfolio_id=portfolio_id,
            symbol=data.symbol,
            quantity=data.quantity,
            avg_buy_price=data.avg_buy_price,
            current_price=data.current_price,
        )
        return HoldingResponse(
            id=holding.id,
            symbol=holding.symbol,
            quantity=holding.quantity,
            avg_buy_price=holding.avg_buy_price,
            current_price=holding.current_price,
            market_value=holding.quantity * holding.current_price,
        )

    async def remove_holding(
        self, portfolio_id: uuid.UUID, holding_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> None:
        await self._get_or_404(portfolio_id, user_id)
        await self.repo.remove_holding(holding_id)

    async def upload_prices(self, data: BulkPriceUpload) -> int:
        prices = [
            {
                "symbol": p.symbol.upper(),
                "date": p.date,
                "open": p.open,
                "high": p.high,
                "low": p.low,
                "close": p.close,
                "volume": p.volume,
            }
            for p in data.prices
        ]
        return await self.price_repo.bulk_upsert(prices)

    async def get_price_history(
        self,
        symbol: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict]:
        prices = await self.price_repo.get_prices(symbol, start_date, end_date)
        return [
            {
                "symbol": p.symbol,
                "date": p.date.isoformat(),
                "close": p.close,
                "volume": p.volume,
            }
            for p in prices
        ]

    async def _get_or_404(
        self, portfolio_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> Portfolio:
        portfolio = await self.repo.get_by_id(portfolio_id, user_id=user_id)
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portfolio {portfolio_id} not found",
            )
        return portfolio

    def _to_response(self, portfolio: Portfolio) -> PortfolioResponse:
        holdings = [
            HoldingResponse(
                id=h.id,
                symbol=h.symbol,
                quantity=h.quantity,
                avg_buy_price=h.avg_buy_price,
                current_price=h.current_price,
                market_value=h.quantity * h.current_price,
            )
            for h in portfolio.holdings
        ]
        total = sum(h.market_value for h in holdings)
        return PortfolioResponse(
            id=portfolio.id,
            name=portfolio.name,
            description=portfolio.description,
            created_at=portfolio.created_at,
            updated_at=portfolio.updated_at,
            holdings=holdings,
            total_value=total,
        )

    def _to_summary(self, portfolio: Portfolio) -> PortfolioSummary:
        total = sum(h.quantity * h.current_price for h in portfolio.holdings)
        return PortfolioSummary(
            id=portfolio.id,
            name=portfolio.name,
            description=portfolio.description,
            created_at=portfolio.created_at,
            holdings_count=len(portfolio.holdings),
            total_value=total,
        )
