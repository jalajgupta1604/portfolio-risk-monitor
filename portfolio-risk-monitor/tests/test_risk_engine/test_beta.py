import numpy as np
import pytest
from numpy.typing import NDArray

from app.risk_engine.beta import downside_beta, portfolio_beta
from app.risk_engine.volatility import compute_log_returns


class TestPortfolioBeta:
    def test_self_beta_is_one(self, benchmark_prices: NDArray[np.float64]) -> None:
        returns = compute_log_returns(benchmark_prices)
        beta = portfolio_beta(returns, returns)
        assert beta == pytest.approx(1.0, abs=1e-6)

    def test_uncorrelated_beta_near_zero(self) -> None:
        rng = np.random.default_rng(42)
        port = rng.normal(0, 0.01, 100)
        bench = rng.normal(0, 0.01, 100)
        beta = portfolio_beta(port, bench)
        assert abs(beta) < 0.3

    def test_positive_beta_for_correlated(self) -> None:
        rng = np.random.default_rng(42)
        bench = rng.normal(0.001, 0.01, 100)
        port = 1.2 * bench + rng.normal(0, 0.002, 100)
        beta = portfolio_beta(port, bench)
        assert beta > 0.8

    def test_short_series(self) -> None:
        port = np.array([0.01])
        bench = np.array([0.02])
        beta = portfolio_beta(port, bench)
        assert beta == 1.0


class TestDownsideBeta:
    def test_downside_returns_value(
        self,
        sample_prices: NDArray[np.float64],
        benchmark_prices: NDArray[np.float64],
    ) -> None:
        port_ret = compute_log_returns(sample_prices)
        bench_ret = compute_log_returns(benchmark_prices)
        n = min(len(port_ret), len(bench_ret))
        db = downside_beta(port_ret[:n], bench_ret[:n])
        assert isinstance(db, float)

    def test_all_positive_market_falls_back(self) -> None:
        port = np.array([0.01, 0.02, 0.015, 0.01, 0.005])
        bench = np.array([0.01, 0.02, 0.015, 0.01, 0.005])
        db = downside_beta(port, bench)
        assert isinstance(db, float)
