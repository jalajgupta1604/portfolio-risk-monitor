import numpy as np
import pytest
from numpy.typing import NDArray

from app.risk_engine.volatility import (
    compute_log_returns,
    portfolio_rolling_volatility,
    rolling_volatility,
)


class TestLogReturns:
    def test_basic_returns(self) -> None:
        prices = np.array([100.0, 105.0, 110.0, 108.0])
        returns = compute_log_returns(prices)
        assert len(returns) == 3
        assert returns[0] == pytest.approx(np.log(105 / 100), rel=1e-10)

    def test_single_price(self) -> None:
        prices = np.array([100.0])
        returns = compute_log_returns(prices)
        assert len(returns) == 0


class TestRollingVolatility:
    def test_returns_positive(self, sample_prices: NDArray[np.float64]) -> None:
        vol = rolling_volatility(sample_prices)
        assert vol > 0

    def test_annualized_greater_than_daily(
        self, sample_prices: NDArray[np.float64]
    ) -> None:
        ann_vol = rolling_volatility(sample_prices, annualize=True)
        daily_vol = rolling_volatility(sample_prices, annualize=False)
        assert ann_vol > daily_vol

    def test_zero_vol_constant_prices(self) -> None:
        prices = np.full(40, 100.0)
        vol = rolling_volatility(prices)
        assert vol == 0.0

    def test_short_series(self) -> None:
        prices = np.array([100.0, 101.0])
        vol = rolling_volatility(prices, window=30)
        assert vol >= 0


class TestPortfolioRollingVolatility:
    def test_returns_positive(
        self,
        multi_asset_prices: NDArray[np.float64],
        equal_weights: NDArray[np.float64],
    ) -> None:
        returns = np.diff(np.log(multi_asset_prices), axis=0)
        vol = portfolio_rolling_volatility(returns, equal_weights)
        assert vol > 0

    def test_single_asset(self) -> None:
        prices = np.array([100.0, 102.0, 101.0, 103.0, 105.0])
        returns = np.diff(np.log(prices)).reshape(-1, 1)
        weights = np.array([1.0])
        vol = portfolio_rolling_volatility(returns, weights, window=3)
        assert vol > 0
