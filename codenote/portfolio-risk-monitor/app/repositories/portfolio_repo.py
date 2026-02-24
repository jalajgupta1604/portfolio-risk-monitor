import uuid
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Holding, Portfolio, PriceHistory


class PortfolioRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, name: str, description: str | None = None) -> Portfolio:
        portfolio = Portfolio(name=name, description=description)
        self.session.add(portfolio)
        await self.session.flush()
        return portfolio

    async def get_by_id(self, portfolio_id: uuid.UUID) -> Portfolio | None:
        stmt = (
            select(Portfolio)
            .options(selectinload(Portfolio.holdings))
            .where(Portfolio.id == portfolio_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Portfolio]:
        stmt = select(Portfolio).order_by(Portfolio.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self,
        portfolio: Portfolio,
        name: str | None = None,
        description: str | None = None,
    ) -> Portfolio:
        if name is not None:
            portfolio.name = name
        if description is not None:
            portfolio.description = description
        await self.session.flush()
        return portfolio

    async def delete(self, portfolio_id: uuid.UUID) -> None:
        stmt = delete(Portfolio).where(Portfolio.id == portfolio_id)
        await self.session.execute(stmt)

    async def add_holding(
        self,
        portfolio_id: uuid.UUID,
        symbol: str,
        quantity: float,
        avg_buy_price: float,
    ) -> Holding:
        holding = Holding(
            portfolio_id=portfolio_id,
            symbol=symbol.upper(),
            quantity=quantity,
            avg_buy_price=avg_buy_price,
        )
        self.session.add(holding)
        await self.session.flush()
        return holding

    async def remove_holding(self, holding_id: uuid.UUID) -> None:
        stmt = delete(Holding).where(Holding.id == holding_id)
        await self.session.execute(stmt)


class PriceHistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def bulk_upsert(self, prices: list[dict]) -> int:
        count = 0
        for p in prices:
            existing = await self._get_by_symbol_date(p["symbol"], p["date"])
            if existing:
                existing.open = p["open"]
                existing.high = p["high"]
                existing.low = p["low"]
                existing.close = p["close"]
                existing.volume = p.get("volume", 0.0)
            else:
                self.session.add(PriceHistory(**p))
            count += 1
        await self.session.flush()
        return count

    async def get_prices(
        self,
        symbol: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[PriceHistory]:
        stmt = (
            select(PriceHistory)
            .where(PriceHistory.symbol == symbol.upper())
            .order_by(PriceHistory.date.asc())
        )
        if start_date:
            stmt = stmt.where(PriceHistory.date >= start_date)
        if end_date:
            stmt = stmt.where(PriceHistory.date <= end_date)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_symbols(self) -> list[str]:
        stmt = select(PriceHistory.symbol).distinct()
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def _get_by_symbol_date(
        self, symbol: str, date: datetime
    ) -> PriceHistory | None:
        stmt = select(PriceHistory).where(
            PriceHistory.symbol == symbol,
            PriceHistory.date == date,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
