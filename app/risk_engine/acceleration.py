import numpy as np
from numpy.typing import NDArray


def risk_acceleration(
    composite_scores: NDArray[np.float64],
    lookback: int = 5,
) -> float:
    n = len(composite_scores)
    if n < 2:
        return 0.0

    if n < lookback:
        lookback = n

    recent = composite_scores[-lookback:]
    deltas = np.diff(recent)
    acceleration = float(np.mean(deltas))
    return round(acceleration, 4)


def generate_early_warnings(
    composite_score: float,
    risk_acceleration_val: float,
    volatility: float,
    beta: float,
    downside_beta: float,
    var_95: float,
    avg_correlation: float,
    sector_weights: dict[str, float] | None = None,
) -> list[str]:
    warnings: list[str] = []

    if composite_score >= 80:
        warnings.append("CRITICAL: Composite risk score exceeds 80 — immediate review required")
    elif composite_score >= 60:
        warnings.append("WARNING: Composite risk score exceeds 60 — elevated risk detected")

    if risk_acceleration_val > 5:
        warnings.append(
            f"ACCELERATION: Risk score increasing rapidly (+{risk_acceleration_val:.1f}/period)"
        )

    if volatility > 0.40:
        warnings.append(f"HIGH VOLATILITY: Annualized vol at {volatility:.1%}")

    if beta > 1.5:
        warnings.append(f"HIGH BETA: Portfolio beta {beta:.2f} — amplified market exposure")

    if downside_beta > beta * 1.3:
        warnings.append(
            f"ASYMMETRIC RISK: Downside beta ({downside_beta:.2f}) significantly exceeds "
            f"upside beta ({beta:.2f})"
        )

    if var_95 > 0.03:
        warnings.append(f"VAR BREACH: Daily 95% VaR at {var_95:.2%} — exceeds 3% threshold")

    if avg_correlation > 0.8:
        warnings.append(
            f"CONCENTRATION: High avg correlation ({avg_correlation:.2f}) — "
            "diversification ineffective"
        )

    if sector_weights:
        for sector, weight in sector_weights.items():
            if weight > 0.40:
                pct = weight * 100
                warnings.append(
                    f"SECTOR CONCENTRATION: {sector} at {pct:.0f}% — exceeds 40% threshold"
                )

    return warnings
