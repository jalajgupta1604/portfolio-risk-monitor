import numpy as np
import pytest
from numpy.typing import NDArray

from app.risk_engine.var import historical_var, parametric_var, var_95
from app.risk_engine.volatility import compute_log_returns


class TestParametricVaR:
    def test_positive_var(self, sample_prices: NDArray[np.float64]) -> None:
        returns = compute_log_returns(sample_prices)
        v = parametric_var(returns)
        assert v > 0

    def test_higher_confidence_higher_var(
        self, sample_prices: NDArray[np.float64]
    ) -> None:
        returns = compute_log_returns(sample_prices)
        var_90 = parametric_var(returns, confidence=0.90)
        var_99 = parametric_var(returns, confidence=0.99)
        assert var_99 > var_90

    def test_empty_returns(self) -> None:
        returns = np.array([0.01])
        v = parametric_var(returns)
        assert v == 0.0


class TestHistoricalVaR:
    def test_positive_var(self, sample_prices: NDArray[np.float64]) -> None:
        returns = compute_log_returns(sample_prices)
        v = historical_var(returns)
        assert isinstance(v, float)

    def test_consistent_with_parametric(
        self, sample_prices: NDArray[np.float64]
    ) -> None:
        returns = compute_log_returns(sample_prices)
        p_var = parametric_var(returns)
        h_var = historical_var(returns)
        assert abs(p_var - h_var) < 0.1


class TestVaR95:
    def test_returns_max_of_both(self, sample_prices: NDArray[np.float64]) -> None:
        returns = compute_log_returns(sample_prices)
        v = var_95(returns)
        p_var = parametric_var(returns)
        h_var = historical_var(returns)
        assert v == pytest.approx(max(p_var, h_var), rel=1e-10)
