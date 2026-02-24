import numpy as np
from numpy.typing import NDArray

from app.schemas.risk import StressScenario

STRESS_SCENARIOS = [-0.03, -0.05, -0.08]


def run_stress_tests(
    portfolio_returns: NDArray[np.float64],
    benchmark_returns: NDArray[np.float64],
    portfolio_value: float,
    beta: float,
    scenarios: list[float] | None = None,
) -> list[StressScenario]:
    if scenarios is None:
        scenarios = STRESS_SCENARIOS

    results: list[StressScenario] = []

    for shock in scenarios:
        portfolio_impact = shock * beta

        if len(portfolio_returns) > 1 and len(benchmark_returns) > 1:
            residual_vol = _residual_volatility(portfolio_returns, benchmark_returns, beta)
            tail_adjustment = residual_vol * 0.5
            portfolio_impact -= abs(tail_adjustment)

        estimated_loss = portfolio_value * portfolio_impact

        results.append(
            StressScenario(
                shock_pct=round(shock * 100, 2),
                portfolio_impact_pct=round(portfolio_impact * 100, 4),
                estimated_loss=round(estimated_loss, 2),
            )
        )

    return results


def _residual_volatility(
    portfolio_returns: NDArray[np.float64],
    benchmark_returns: NDArray[np.float64],
    beta: float,
) -> float:
    n = min(len(portfolio_returns), len(benchmark_returns))
    pr = portfolio_returns[-n:]
    br = benchmark_returns[-n:]
    residuals = pr - beta * br
    return float(np.std(residuals, ddof=1))
