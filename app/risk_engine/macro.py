"""Macro factor sensitivity analysis via rolling correlation."""

import numpy as np
from numpy.typing import NDArray

MACRO_FACTORS: dict[str, str] = {
    "CL=F": "Crude Oil",
    "USDINR=X": "USD/INR",
    "^TNX": "US 10Y Yield",
    "GC=F": "Gold",
}


def compute_macro_sensitivities(
    portfolio_returns: NDArray[np.float64],
    factor_price_series: dict[str, NDArray[np.float64]],
    window: int = 30,
) -> dict[str, float]:
    """Compute rolling correlation between portfolio returns and each macro factor.

    Returns a dict mapping factor display name → correlation coefficient.
    """
    result: dict[str, float] = {}

    for symbol, prices in factor_price_series.items():
        if len(prices) < 3:
            continue
        factor_returns = np.diff(np.log(prices))

        # Align lengths
        min_len = min(len(portfolio_returns), len(factor_returns))
        if min_len < window:
            # Use whatever we have
            pr = portfolio_returns[-min_len:]
            fr = factor_returns[-min_len:]
        else:
            pr = portfolio_returns[-window:]
            fr = factor_returns[-window:]

        if len(pr) < 5 or np.std(pr) == 0 or np.std(fr) == 0:
            continue

        corr = float(np.corrcoef(pr, fr)[0, 1])
        display_name = MACRO_FACTORS.get(symbol, symbol)
        result[display_name] = round(corr, 4)

    return result
