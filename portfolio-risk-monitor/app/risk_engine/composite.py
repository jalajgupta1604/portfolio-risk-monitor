import numpy as np

from app.config import settings
from app.schemas.risk import RiskLevel


def compute_composite_score(
    volatility: float,
    var_95: float,
    beta: float,
    downside_beta: float,
    avg_correlation: float,
    worst_stress_impact: float,
) -> float:
    vol_score = _normalize_volatility(volatility)
    var_score = _normalize_var(var_95)
    beta_score = _normalize_beta(beta)
    downside_score = _normalize_beta(downside_beta)
    corr_score = _normalize_correlation(avg_correlation)
    stress_score = _normalize_stress(worst_stress_impact)

    composite = (
        settings.RISK_WEIGHT_VOLATILITY * vol_score
        + settings.RISK_WEIGHT_VAR * var_score
        + settings.RISK_WEIGHT_BETA * beta_score
        + settings.RISK_WEIGHT_DOWNSIDE_BETA * downside_score
        + settings.RISK_WEIGHT_CORRELATION * corr_score
        + settings.RISK_WEIGHT_STRESS * stress_score
    )

    return float(np.clip(composite, 0, 100))


def classify_risk_level(score: float) -> RiskLevel:
    if score < 20:
        return RiskLevel.LOW
    if score < 40:
        return RiskLevel.MODERATE
    if score < 60:
        return RiskLevel.ELEVATED
    if score < 80:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def _normalize_volatility(vol: float) -> float:
    return float(np.clip((vol / 0.60) * 100, 0, 100))


def _normalize_var(var: float) -> float:
    return float(np.clip((var / 0.05) * 100, 0, 100))


def _normalize_beta(beta: float) -> float:
    return float(np.clip((abs(beta) / 2.0) * 100, 0, 100))


def _normalize_correlation(corr: float) -> float:
    return float(np.clip(((corr + 1) / 2) * 100, 0, 100))


def _normalize_stress(impact: float) -> float:
    return float(np.clip((abs(impact) / 0.15) * 100, 0, 100))
