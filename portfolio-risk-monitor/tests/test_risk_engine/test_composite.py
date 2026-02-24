import pytest

from app.risk_engine.composite import classify_risk_level, compute_composite_score
from app.schemas.risk import RiskLevel


class TestCompositeScore:
    def test_score_in_range(self) -> None:
        score = compute_composite_score(
            volatility=0.25,
            var_95=0.02,
            beta=1.1,
            downside_beta=1.3,
            avg_correlation=0.5,
            worst_stress_impact=-0.05,
        )
        assert 0 <= score <= 100

    def test_zero_risk(self) -> None:
        score = compute_composite_score(
            volatility=0.0,
            var_95=0.0,
            beta=0.0,
            downside_beta=0.0,
            avg_correlation=-1.0,
            worst_stress_impact=0.0,
        )
        assert score == 0.0

    def test_extreme_risk(self) -> None:
        score = compute_composite_score(
            volatility=1.0,
            var_95=0.10,
            beta=3.0,
            downside_beta=3.0,
            avg_correlation=1.0,
            worst_stress_impact=-0.30,
        )
        assert score == 100.0

    def test_moderate_inputs(self) -> None:
        score = compute_composite_score(
            volatility=0.20,
            var_95=0.015,
            beta=1.0,
            downside_beta=1.0,
            avg_correlation=0.3,
            worst_stress_impact=-0.04,
        )
        assert 20 < score < 60


class TestRiskLevel:
    @pytest.mark.parametrize(
        "score,expected",
        [
            (10, RiskLevel.LOW),
            (30, RiskLevel.MODERATE),
            (50, RiskLevel.ELEVATED),
            (70, RiskLevel.HIGH),
            (90, RiskLevel.CRITICAL),
        ],
    )
    def test_classification(self, score: float, expected: RiskLevel) -> None:
        assert classify_risk_level(score) == expected
