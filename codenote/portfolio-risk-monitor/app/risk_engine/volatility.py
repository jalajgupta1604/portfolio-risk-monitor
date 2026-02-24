import numpy as np
from numpy.typing import NDArray

from app.config import settings


def compute_log_returns(prices: NDArray[np.float64]) -> NDArray[np.float64]:
    return np.diff(np.log(prices))


def rolling_volatility(
    prices: NDArray[np.float64],
    window: int = settings.ROLLING_WINDOW,
    annualize: bool = True,
) -> float:
    returns = compute_log_returns(prices)
    if len(returns) < window:
        window = len(returns)
    if window < 2:
        return 0.0

    rolling_std = np.std(returns[-window:], ddof=1)
    if annualize:
        return float(rolling_std * np.sqrt(settings.TRADING_DAYS_PER_YEAR))
    return float(rolling_std)


def portfolio_rolling_volatility(
    returns_matrix: NDArray[np.float64],
    weights: NDArray[np.float64],
    window: int = settings.ROLLING_WINDOW,
) -> float:
    T = returns_matrix.shape[0]
    if T < window:
        window = T
    if window == 0:
        return 0.0

    windowed = returns_matrix[-window:]
    cov_matrix = np.cov(windowed, rowvar=False)

    if cov_matrix.ndim == 0:
        port_var = float(cov_matrix) * weights[0] ** 2
    else:
        port_var = float(weights @ cov_matrix @ weights)

    annualized_vol = np.sqrt(port_var * settings.TRADING_DAYS_PER_YEAR)
    return float(annualized_vol)
