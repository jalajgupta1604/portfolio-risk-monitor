import numpy as np
import pytest
from numpy.typing import NDArray

from app.risk_engine.core import RiskComputationInput, RiskEngine
from app.schemas.risk import RiskLevel


class TestRiskEngine:
    @pytest.fixture
    def engine(self) -> RiskEngine:
        return RiskEngine(window=30)

    @pytest.fixture
    def computation_input(
        self,
        multi_asset_prices: NDArray[np.float64],
        benchmark_prices: NDArray[np.float64],
    ) -> RiskComputationInput:
        n = min(multi_asset_prices.shape[0], len(benchmark_prices))
        return RiskComputationInput(
            price_matrix=multi_asset_prices[:n],
            benchmark_prices=benchmark_prices[:n],
            weights=np.array([0.4, 0.3, 0.3]),
            symbols=["STOCK_A", "STOCK_B", "STOCK_C"],
            portfolio_value=1_000_000.0,
        )

    def test_compute_returns_result(
        self,
        engine: RiskEngine,
        computation_input: RiskComputationInput,
    ) -> None:
        result = engine.compute(computation_input)
        assert result.rolling_volatility > 0
        assert isinstance(result.beta, float)
        assert isinstance(result.downside_beta_val, float)
        assert result.var_95_pct > 0
        assert 0 <= result.composite_score <= 100
        assert result.risk_level in RiskLevel
        assert len(result.stress_scenarios) == 3
        assert len(result.correlation_map) == 3

    def test_var_amount_matches(
        self,
        engine: RiskEngine,
        computation_input: RiskComputationInput,
    ) -> None:
        result = engine.compute(computation_input)
        expected = result.var_95_pct * computation_input.portfolio_value
        assert result.var_95_amount == pytest.approx(expected, rel=1e-2)

    def test_weights_map(
        self,
        engine: RiskEngine,
        computation_input: RiskComputationInput,
    ) -> None:
        result = engine.compute(computation_input)
        assert len(result.weights_map) == 3
        assert sum(result.weights_map.values()) == pytest.approx(1.0, abs=1e-6)

    def test_with_historical_scores(
        self,
        engine: RiskEngine,
        computation_input: RiskComputationInput,
    ) -> None:
        inp = RiskComputationInput(
            price_matrix=computation_input.price_matrix,
            benchmark_prices=computation_input.benchmark_prices,
            weights=computation_input.weights,
            symbols=computation_input.symbols,
            portfolio_value=computation_input.portfolio_value,
            historical_composite_scores=np.array([30.0, 35.0, 40.0, 42.0, 45.0]),
        )
        result = engine.compute(inp)
        assert isinstance(result.risk_acceleration_val, float)
