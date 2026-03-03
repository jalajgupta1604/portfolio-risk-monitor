import logging
import uuid

import numpy as np
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import RiskSnapshot
from app.repositories import PortfolioRepository, PriceHistoryRepository, RiskSnapshotRepository
from app.risk_engine import RiskComputationInput, RiskEngine
from app.schemas.risk import RiskHistoryEntry, RiskHistoryResponse, RiskReportResponse
from app.services.stock_service import StockService

logger = logging.getLogger(__name__)


class RiskService:
    def __init__(self, session: AsyncSession) -> None:
        self.portfolio_repo = PortfolioRepository(session)
        self.price_repo = PriceHistoryRepository(session)
        self.risk_repo = RiskSnapshotRepository(session)
        self.engine = RiskEngine()

    async def compute_risk(self, portfolio_id: uuid.UUID) -> RiskReportResponse:
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portfolio {portfolio_id} not found",
            )

        if not portfolio.holdings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Portfolio has no holdings",
            )

        # Auto-refresh current prices from yfinance for any holding at 0
        for holding in portfolio.holdings:
            if holding.current_price <= 0:
                try:
                    quote = await StockService.get_quote(holding.symbol)
                    if quote.last_price > 0:
                        holding.current_price = quote.last_price
                except Exception:
                    logger.warning("Failed to fetch quote for %s", holding.symbol)

        symbols = [h.symbol for h in portfolio.holdings]
        quantities = np.array([h.quantity for h in portfolio.holdings])
        current_prices = np.array([h.current_price for h in portfolio.holdings])

        market_values = quantities * current_prices
        total_value = float(np.sum(market_values))

        if total_value <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Portfolio has zero market value. Update current prices first.",
            )

        weights = market_values / total_value

        # Compute sector allocation from holdings
        sector_totals: dict[str, float] = {}
        for h, mv in zip(portfolio.holdings, market_values):
            sector = h.sector or "Unknown"
            sector_totals[sector] = sector_totals.get(sector, 0.0) + float(mv)
        sector_allocation = {s: v / total_value for s, v in sector_totals.items()} if total_value > 0 else {}

        # Auto-fetch missing price history from yfinance
        all_symbols = symbols + [settings.NIFTY_SYMBOL]
        for sym in all_symbols:
            prices = await self.price_repo.get_prices(sym)
            if len(prices) < 2:
                try:
                    logger.info("Fetching price history for %s from yfinance", sym)
                    records = await StockService.fetch_history(sym, period="1y")
                    if records:
                        await self.price_repo.bulk_upsert(records)
                except Exception:
                    logger.warning("Failed to fetch price history for %s", sym)

        price_series = {}
        for sym in symbols:
            prices = await self.price_repo.get_prices(sym)
            if len(prices) < 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient price history for {sym}. Need at least 2 data points.",
                )
            price_series[sym] = np.array([p.close for p in prices])

        benchmark_prices_raw = await self.price_repo.get_prices(settings.NIFTY_SYMBOL)
        if len(benchmark_prices_raw) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient NIFTY benchmark data. Upload benchmark prices first.",
            )
        benchmark_prices = np.array([p.close for p in benchmark_prices_raw])

        min_len = min(len(v) for v in price_series.values())
        min_len = min(min_len, len(benchmark_prices))
        price_matrix = np.column_stack(
            [price_series[sym][-min_len:] for sym in symbols]
        )
        benchmark_prices = benchmark_prices[-min_len:]

        historical_scores = await self.risk_repo.get_composite_scores(portfolio_id)
        hist_scores = np.array(historical_scores) if historical_scores else None

        inp = RiskComputationInput(
            price_matrix=price_matrix,
            benchmark_prices=benchmark_prices,
            weights=weights,
            symbols=symbols,
            portfolio_value=total_value,
            historical_composite_scores=hist_scores,
            sector_weights=sector_allocation if sector_allocation else None,
        )

        result = self.engine.compute(inp)

        snapshot = RiskSnapshot(
            portfolio_id=portfolio_id,
            rolling_volatility=result.rolling_volatility,
            portfolio_beta=result.beta,
            downside_beta=result.downside_beta_val,
            var_95=result.var_95_pct,
            composite_score=result.composite_score,
            risk_acceleration=result.risk_acceleration_val,
            risk_level=result.risk_level.value,
            sector_concentration=result.sector_concentration,
            correlation_matrix=result.correlation_map,
            stress_results=[s.model_dump() for s in result.stress_scenarios],
            weights=result.weights_map,
        )
        await self.risk_repo.create(snapshot)

        # Fetch India VIX (best-effort)
        india_vix: float | None = None
        try:
            vix_prices = await self.price_repo.get_prices(settings.INDIA_VIX_SYMBOL)
            if vix_prices:
                india_vix = vix_prices[-1].close
            else:
                vix_records = await StockService.fetch_history(settings.INDIA_VIX_SYMBOL, period="5d")
                if vix_records:
                    india_vix = vix_records[-1]["close"]
        except Exception:
            logger.warning("Failed to fetch India VIX")

        # VIX spike warning
        early_warnings = list(result.early_warnings)
        if india_vix is not None and india_vix > settings.VIX_SPIKE_THRESHOLD:
            early_warnings.append(
                f"VIX SPIKE: India VIX at {india_vix:.1f} — exceeds {settings.VIX_SPIKE_THRESHOLD:.0f} threshold"
            )

        return RiskReportResponse(
            portfolio_id=portfolio_id,
            computed_at=snapshot.computed_at,
            rolling_volatility=result.rolling_volatility,
            portfolio_beta=result.beta,
            downside_beta=result.downside_beta_val,
            var_95=result.var_95_pct,
            var_95_amount=result.var_95_amount,
            composite_score=result.composite_score,
            risk_level=result.risk_level,
            risk_acceleration=result.risk_acceleration_val,
            correlation_matrix=result.correlation_map,
            stress_results=result.stress_scenarios,
            weights=result.weights_map,
            total_portfolio_value=total_value,
            early_warning_signals=early_warnings,
            sector_allocation=sector_allocation,
            sector_concentration=result.sector_concentration,
            india_vix=india_vix,
        )

    async def get_risk_history(
        self, portfolio_id: uuid.UUID, limit: int = 100
    ) -> RiskHistoryResponse:
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portfolio {portfolio_id} not found",
            )

        snapshots = await self.risk_repo.get_history(portfolio_id, limit)
        entries = [
            RiskHistoryEntry(
                id=s.id,
                computed_at=s.computed_at,
                composite_score=s.composite_score,
                risk_level=s.risk_level,
                rolling_volatility=s.rolling_volatility,
                var_95=s.var_95,
                portfolio_beta=s.portfolio_beta,
                risk_acceleration=s.risk_acceleration,
            )
            for s in snapshots
        ]
        return RiskHistoryResponse(
            portfolio_id=portfolio_id,
            entries=entries,
            count=len(entries),
        )
