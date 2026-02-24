import numpy as np
from numpy.typing import NDArray

from app.config import settings


def portfolio_beta(
    portfolio_returns: NDArray[np.float64],
    benchmark_returns: NDArray[np.float64],
    window: int = settings.ROLLING_WINDOW,
) -> float:
    n = min(len(portfolio_returns), len(benchmark_returns))
    if n < 2:
        return 1.0

    if n < window:
        window = n

    pr = portfolio_returns[-window:]
    br = benchmark_returns[-window:]

    cov_matrix = np.cov(pr, br)
    benchmark_var = cov_matrix[1, 1]

    if benchmark_var == 0:
        return 1.0

    return float(cov_matrix[0, 1] / benchmark_var)


def downside_beta(
    portfolio_returns: NDArray[np.float64],
    benchmark_returns: NDArray[np.float64],
    window: int = settings.ROLLING_WINDOW,
) -> float:
    n = min(len(portfolio_returns), len(benchmark_returns))
    if n < 2:
        return 1.0

    if n < window:
        window = n

    pr = portfolio_returns[-window:]
    br = benchmark_returns[-window:]

    downside_mask = br < 0
    if np.sum(downside_mask) < 2:
        return portfolio_beta(portfolio_returns, benchmark_returns, window)

    pr_down = pr[downside_mask]
    br_down = br[downside_mask]

    cov_matrix = np.cov(pr_down, br_down)
    benchmark_var = cov_matrix[1, 1]

    if benchmark_var == 0:
        return 1.0

    return float(cov_matrix[0, 1] / benchmark_var)
