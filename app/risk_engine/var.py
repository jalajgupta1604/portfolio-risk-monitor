import numpy as np
from numpy.typing import NDArray
from scipy import stats

from app.config import settings


def parametric_var(
    portfolio_returns: NDArray[np.float64],
    confidence: float = settings.VAR_CONFIDENCE,
    window: int = settings.ROLLING_WINDOW,
) -> float:
    n = len(portfolio_returns)
    if n < 2:
        return 0.0

    if n < window:
        window = n

    windowed = portfolio_returns[-window:]
    mu = np.mean(windowed)
    sigma = np.std(windowed, ddof=1)
    z_score = stats.norm.ppf(1 - confidence)

    return float(-(mu + z_score * sigma))


def historical_var(
    portfolio_returns: NDArray[np.float64],
    confidence: float = settings.VAR_CONFIDENCE,
    window: int = settings.ROLLING_WINDOW,
) -> float:
    n = len(portfolio_returns)
    if n < 2:
        return 0.0

    if n < window:
        window = n

    windowed = portfolio_returns[-window:]
    percentile = (1 - confidence) * 100
    return float(-np.percentile(windowed, percentile))


def var_95(
    portfolio_returns: NDArray[np.float64],
    window: int = settings.ROLLING_WINDOW,
) -> float:
    p_var = parametric_var(portfolio_returns, settings.VAR_CONFIDENCE, window)
    h_var = historical_var(portfolio_returns, settings.VAR_CONFIDENCE, window)
    return float(max(p_var, h_var))
