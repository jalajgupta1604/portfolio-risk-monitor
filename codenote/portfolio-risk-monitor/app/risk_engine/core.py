from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from app.config import settings
from app.risk_engine.acceleration import generate_early_warnings, risk_acceleration
from app.risk_engine.beta import downside_beta, portfolio_beta
from app.risk_engine.composite import classify_risk_level, compute_composite_score
from app.risk_engine.correlation import avg_pairwise_correlation, correlation_matrix
from app.risk_engine.stress import run_stress_tests
from app.risk_engine.var import var_95
from app.risk_engine.volatility import compute_log_returns, portfolio_rolling_volatility
from app.schemas.risk import RiskLevel, StressScenario


@dataclass(frozen=True)
class RiskComputationInput:
    price_matrix: NDArray[np.float64]
    benchmark_prices: NDArray[np.float64]
    weights: NDArray[np.float64]
    symbols: list[str]
    portfolio_value: float
    historical_composite_scores: NDArray[np.float64] | None = None


@dataclass(frozen=True)
class RiskComputationResult:
    rolling_volatility: float
    correlation_map: dict[str, dict[str, float]]
    avg_correlation: float
    beta: float
    downside_beta_val: float
    var_95_pct: float
    var_95_amount: float
    stress_scenarios: list[StressScenario]
    composite_score: float
    risk_level: RiskLevel
    risk_acceleration_val: float
    early_warnings: list[str]
    weights_map: dict[str, float]


class RiskEngine:
    def __init__(self, window: int = settings.ROLLING_WINDOW) -> None:
        self.window = window

    def compute(self, inp: RiskComputationInput) -> RiskComputationResult:
        n_assets = inp.price_matrix.shape[1]
        returns_matrix = np.column_stack(
            [compute_log_returns(inp.price_matrix[:, i]) for i in range(n_assets)]
        )
        benchmark_returns = compute_log_returns(inp.benchmark_prices)

        portfolio_returns = returns_matrix @ inp.weights

        vol = portfolio_rolling_volatility(returns_matrix, inp.weights, self.window)
        corr_map = correlation_matrix(returns_matrix, inp.symbols, self.window)
        avg_corr = avg_pairwise_correlation(returns_matrix, self.window)
        b = portfolio_beta(portfolio_returns, benchmark_returns, self.window)
        db = downside_beta(portfolio_returns, benchmark_returns, self.window)
        v95 = var_95(portfolio_returns, self.window)
        v95_amount = v95 * inp.portfolio_value

        stress = run_stress_tests(
            portfolio_returns, benchmark_returns, inp.portfolio_value, b
        )

        worst_stress = min(s.portfolio_impact_pct for s in stress) / 100.0 if stress else 0.0

        composite = compute_composite_score(
            volatility=vol,
            var_95=v95,
            beta=b,
            downside_beta=db,
            avg_correlation=avg_corr,
            worst_stress_impact=worst_stress,
        )

        level = classify_risk_level(composite)

        accel = 0.0
        if inp.historical_composite_scores is not None and len(inp.historical_composite_scores) > 0:
            scores_with_current = np.append(inp.historical_composite_scores, composite)
            accel = risk_acceleration(scores_with_current)

        warnings = generate_early_warnings(
            composite_score=composite,
            risk_acceleration_val=accel,
            volatility=vol,
            beta=b,
            downside_beta=db,
            var_95=v95,
            avg_correlation=avg_corr,
        )

        weights_map = {sym: float(w) for sym, w in zip(inp.symbols, inp.weights)}

        return RiskComputationResult(
            rolling_volatility=round(vol, 6),
            correlation_map=corr_map,
            avg_correlation=round(avg_corr, 6),
            beta=round(b, 6),
            downside_beta_val=round(db, 6),
            var_95_pct=round(v95, 6),
            var_95_amount=round(v95_amount, 2),
            stress_scenarios=stress,
            composite_score=round(composite, 2),
            risk_level=level,
            risk_acceleration_val=accel,
            early_warnings=warnings,
            weights_map=weights_map,
        )
