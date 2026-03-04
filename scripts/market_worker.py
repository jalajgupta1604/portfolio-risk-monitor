"""
Production Market Data Worker

Fetches real market prices from Yahoo Finance, updates the database,
refreshes current_price on holdings, and auto-computes risk for all portfolios.

Usage:
  # One-shot run (for cron / systemd timer)
  python -m scripts.market_worker

  # Continuous loop (for Docker / long-running process)
  python -m scripts.market_worker --loop --interval 3600

Schedule with cron for real production:
  # Run every day at 6:00 PM IST (after market close)
  30 12 * * 1-5 cd /app && python -m scripts.market_worker >> /var/log/market_worker.log 2>&1
"""

import argparse
import asyncio
import logging
import time
import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import httpx
import yfinance as yf
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models import Holding, Portfolio, PriceHistory
from app.services.alert_service import send_alerts
from app.services.risk_service import RiskService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("market_worker")


def is_market_hours() -> bool:
    """Check if Indian stock market is currently open (IST 9:15-15:30, Mon-Fri)."""
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return market_open <= now <= market_close


async def get_engine_and_session():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return engine, session_factory


async def fetch_and_store_prices(session: AsyncSession) -> dict[str, float]:
    """Fetch real prices from Yahoo Finance for all symbols in the DB."""

    # 1. Collect all unique symbols from holdings + benchmark
    stmt = select(Holding.symbol).distinct()
    result = await session.execute(stmt)
    symbols = list(result.scalars().all())

    benchmark = settings.NIFTY_SYMBOL
    vix = settings.INDIA_VIX_SYMBOL
    macro_symbols = ["CL=F", "USDINR=X", "^TNX", "GC=F"]
    all_symbols = list(set(symbols + [benchmark, vix] + macro_symbols))

    if not all_symbols:
        logger.warning("No symbols found in holdings.")
        return {}

    logger.info("Fetching prices for %d symbols: %s", len(all_symbols), all_symbols)

    # 2. Download from Yahoo Finance (last 100 days to fill gaps)
    tickers_str = " ".join(all_symbols)
    data = yf.download(tickers_str, period="100d", group_by="ticker", progress=False)

    latest_prices: dict[str, float] = {}
    upsert_count = 0

    for symbol in all_symbols:
        try:
            if len(all_symbols) == 1:
                df = data  # single ticker returns flat DataFrame
            else:
                df = data[symbol]

            df = df.dropna(subset=["Close"])
            if df.empty:
                logger.warning("No data returned for %s", symbol)
                continue

            for date_idx, row in df.iterrows():
                dt = datetime(date_idx.year, date_idx.month, date_idx.day, tzinfo=timezone.utc)
                close_val = float(row["Close"])

                # Check if record exists
                existing = await session.execute(
                    select(PriceHistory).where(
                        PriceHistory.symbol == symbol,
                        PriceHistory.date == dt,
                    )
                )
                existing_row = existing.scalar_one_or_none()

                if existing_row:
                    existing_row.open = float(row["Open"])
                    existing_row.high = float(row["High"])
                    existing_row.low = float(row["Low"])
                    existing_row.close = close_val
                    existing_row.volume = float(row.get("Volume", 0))
                else:
                    session.add(PriceHistory(
                        id=uuid.uuid4(),
                        symbol=symbol,
                        date=dt,
                        open=float(row["Open"]),
                        high=float(row["High"]),
                        low=float(row["Low"]),
                        close=close_val,
                        volume=float(row.get("Volume", 0)),
                    ))
                upsert_count += 1

            # Track latest close for updating holdings
            latest_prices[symbol] = float(df.iloc[-1]["Close"])
            logger.info("  %s: %d rows, latest=%.2f", symbol, len(df), latest_prices[symbol])

        except Exception as e:
            logger.error("Failed to process %s: %s", symbol, e)

    await session.flush()
    logger.info("Upserted %d price records total.", upsert_count)
    return latest_prices


async def update_holding_prices(session: AsyncSession, latest_prices: dict[str, float]) -> int:
    """Update current_price on all holdings with latest market data."""
    updated = 0
    for symbol, price in latest_prices.items():
        stmt = (
            update(Holding)
            .where(Holding.symbol == symbol)
            .values(current_price=price)
        )
        result = await session.execute(stmt)
        updated += result.rowcount
    await session.flush()
    logger.info("Updated current_price for %d holdings.", updated)
    return updated


async def compute_risk_all_portfolios(session: AsyncSession) -> int:
    """Run risk computation for every portfolio that has holdings."""
    stmt = (
        select(Portfolio)
        .options(selectinload(Portfolio.holdings), selectinload(Portfolio.owner))
    )
    result = await session.execute(stmt)
    portfolios = list(result.scalars().all())

    computed = 0
    for portfolio in portfolios:
        if not portfolio.holdings:
            logger.info("Skipping %s (no holdings)", portfolio.name)
            continue

        try:
            risk_service = RiskService(session)
            report = await risk_service.compute_risk(portfolio.id)
            await session.commit()
            logger.info(
                "  %s → score=%.1f level=%s volatility=%.2f%% VaR=%.2f%%",
                portfolio.name,
                report.composite_score,
                report.risk_level.value,
                report.rolling_volatility * 100,
                report.var_95 * 100,
            )

            # Log early warnings
            if report.early_warning_signals:
                for signal in report.early_warning_signals:
                    logger.warning("  ALERT [%s]: %s", portfolio.name, signal)

            # Send alerts (email + webhook + WhatsApp) if risk level qualifies
            owner = portfolio.owner
            await send_alerts(
                portfolio_name=portfolio.name,
                portfolio_id=str(portfolio.id),
                risk_level=report.risk_level.value,
                composite_score=report.composite_score,
                signals=report.early_warning_signals,
                user_phone=getattr(owner, "phone_number", None) if owner else None,
                whatsapp_enabled=getattr(owner, "whatsapp_alerts_enabled", False) if owner else False,
            )

            # Notify WebSocket clients via API (fail silently if API not running)
            try:
                notify_url = f"{settings.API_BASE_URL}/api/v1/ws/notify/{portfolio.id}"
                async with httpx.AsyncClient(timeout=5) as client:
                    await client.post(notify_url, json=report.model_dump(mode="json"))
                    logger.info("  WS notify sent for %s", portfolio.name)
            except Exception:
                logger.debug("  WS notify skipped (API server not reachable)")

            computed += 1
        except Exception as e:
            logger.error("  Risk computation failed for %s: %s", portfolio.name, e)

    return computed


async def run_once():
    """Single execution: fetch prices → update holdings → compute risk."""
    # Skip weekends (Saturday=5, Sunday=6)
    if datetime.now(timezone.utc).weekday() >= 5:
        logger.info("Weekend — skipping market data fetch.")
        return

    start = time.time()
    logger.info("=" * 60)
    logger.info("Market Worker started at %s", datetime.now(timezone.utc).isoformat())
    logger.info("=" * 60)

    engine, session_factory = await get_engine_and_session()

    async with session_factory() as session:
        # Step 1: Fetch real market prices
        logger.info("[Step 1/3] Fetching market prices from Yahoo Finance...")
        latest_prices = await fetch_and_store_prices(session)
        await session.commit()

        # Step 2: Update holding current prices
        logger.info("[Step 2/3] Updating holding prices...")
        await update_holding_prices(session, latest_prices)
        await session.commit()

        # Step 3: Compute risk for all portfolios
        logger.info("[Step 3/3] Computing risk for all portfolios...")
        computed = await compute_risk_all_portfolios(session)

    await engine.dispose()

    elapsed = time.time() - start
    logger.info("=" * 60)
    logger.info("Done. %d portfolios processed in %.1fs", computed, elapsed)
    logger.info("=" * 60)


async def run_loop(interval: int | None = None):
    """Continuous loop with dynamic interval based on market hours."""
    while True:
        try:
            await run_once()
        except Exception as e:
            logger.error("Worker loop error: %s", e)
        if interval is not None:
            sleep_secs = interval
        elif is_market_hours():
            sleep_secs = settings.INTRADAY_INTERVAL
        else:
            sleep_secs = settings.EOD_INTERVAL
        logger.info("Sleeping %d seconds until next run... (market_hours=%s)", sleep_secs, is_market_hours())
        await asyncio.sleep(sleep_secs)


def main():
    parser = argparse.ArgumentParser(description="Market Data Worker")
    parser.add_argument("--loop", action="store_true", help="Run continuously in a loop")
    parser.add_argument("--interval", type=int, default=None, help="Fixed seconds between runs (omit for dynamic market-hours interval)")
    args = parser.parse_args()

    if args.loop:
        asyncio.run(run_loop(args.interval))
    else:
        asyncio.run(run_once())


if __name__ == "__main__":
    main()
