"""Seed the database with sample portfolio and synthetic price data."""
import asyncio
import uuid
from datetime import datetime, timedelta, timezone

import numpy as np
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.database import Base
from app.models import Holding, Portfolio, PriceHistory

SYMBOLS = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS"]
BENCHMARK = settings.NIFTY_SYMBOL

BASE_PRICES = {
    "RELIANCE.NS": 2500.0,
    "TCS.NS": 3800.0,
    "HDFCBANK.NS": 1650.0,
    "INFY.NS": 1500.0,
    "ICICIBANK.NS": 1100.0,
    BENCHMARK: 22000.0,
}

DAILY_VOLS = {
    "RELIANCE.NS": 0.018,
    "TCS.NS": 0.015,
    "HDFCBANK.NS": 0.016,
    "INFY.NS": 0.020,
    "ICICIBANK.NS": 0.017,
    BENCHMARK: 0.012,
}


def generate_price_series(
    symbol: str, days: int = 90, seed: int = 42
) -> list[dict]:
    rng = np.random.default_rng(seed + hash(symbol) % 1000)
    base = BASE_PRICES[symbol]
    vol = DAILY_VOLS[symbol]

    returns = rng.normal(0.0003, vol, days)
    prices = base * np.exp(np.cumsum(returns))

    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    records = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        if date.weekday() >= 5:
            continue
        close = float(prices[i])
        daily_range = close * rng.uniform(0.005, 0.02)
        records.append(
            {
                "id": uuid.uuid4(),
                "symbol": symbol,
                "date": date,
                "open": round(close - daily_range * rng.uniform(-0.5, 0.5), 2),
                "high": round(close + daily_range * 0.5, 2),
                "low": round(close - daily_range * 0.5, 2),
                "close": round(close, 2),
                "volume": round(float(rng.uniform(1e6, 5e7)), 0),
            }
        )
    return records


async def seed() -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        existing = await session.execute(text("SELECT count(*) FROM portfolios"))
        if existing.scalar_one() > 0:
            print("Database already seeded. Skipping.")
            return

        await _seed_data(session)
        await session.commit()
        print("Seed completed successfully.")

    await engine.dispose()


async def _seed_data(session: AsyncSession) -> None:
    portfolio = Portfolio(
        name="Indian Large Cap Growth",
        description="Diversified large-cap portfolio tracking top NIFTY constituents",
    )
    session.add(portfolio)
    await session.flush()

    holdings_data = [
        ("RELIANCE.NS", 40, 2450.0),
        ("TCS.NS", 25, 3750.0),
        ("HDFCBANK.NS", 60, 1600.0),
        ("INFY.NS", 50, 1480.0),
        ("ICICIBANK.NS", 80, 1050.0),
    ]

    all_prices = {}
    for symbol in SYMBOLS + [BENCHMARK]:
        price_records = generate_price_series(symbol)
        all_prices[symbol] = price_records
        for rec in price_records:
            session.add(PriceHistory(**rec))

    for symbol, qty, avg_price in holdings_data:
        latest_close = all_prices[symbol][-1]["close"]
        holding = Holding(
            portfolio_id=portfolio.id,
            symbol=symbol,
            quantity=qty,
            avg_buy_price=avg_price,
            current_price=latest_close,
        )
        session.add(holding)

    print(f"Created portfolio: {portfolio.name} ({portfolio.id})")
    print(f"Added {len(holdings_data)} holdings")
    total_prices = sum(len(v) for v in all_prices.values())
    print(f"Inserted {total_prices} price records across {len(all_prices)} symbols")


if __name__ == "__main__":
    asyncio.run(seed())
