import numpy as np
from numpy.typing import NDArray

from app.config import settings


def correlation_matrix(
    returns_matrix: NDArray[np.float64],
    symbols: list[str],
    window: int = settings.ROLLING_WINDOW,
) -> dict[str, dict[str, float]]:
    T = returns_matrix.shape[0]
    if T < 2:
        return {s: {s2: 0.0 for s2 in symbols} for s in symbols}

    if T < window:
        window = T

    windowed = returns_matrix[-window:]
    corr = np.corrcoef(windowed, rowvar=False)

    if corr.ndim == 0:
        return {symbols[0]: {symbols[0]: 1.0}}

    result: dict[str, dict[str, float]] = {}
    for i, sym_i in enumerate(symbols):
        result[sym_i] = {}
        for j, sym_j in enumerate(symbols):
            result[sym_i][sym_j] = round(float(corr[i, j]), 6)

    return result


def avg_pairwise_correlation(
    returns_matrix: NDArray[np.float64],
    window: int = settings.ROLLING_WINDOW,
) -> float:
    T = returns_matrix.shape[0]
    n = returns_matrix.shape[1]
    if T < 2 or n < 2:
        return 0.0

    if T < window:
        window = T

    windowed = returns_matrix[-window:]
    corr = np.corrcoef(windowed, rowvar=False)
    mask = ~np.eye(n, dtype=bool)
    return float(np.mean(corr[mask]))
