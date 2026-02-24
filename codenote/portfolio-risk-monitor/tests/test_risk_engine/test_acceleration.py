import numpy as np

from app.risk_engine.acceleration import generate_early_warnings, risk_acceleration


class TestRiskAcceleration:
    def test_increasing_scores(self) -> None:
        scores = np.array([20.0, 25.0, 30.0, 35.0, 40.0])
        accel = risk_acceleration(scores)
        assert accel > 0

    def test_decreasing_scores(self) -> None:
        scores = np.array([50.0, 45.0, 40.0, 35.0, 30.0])
        accel = risk_acceleration(scores)
        assert accel < 0

    def test_stable_scores(self) -> None:
        scores = np.array([30.0, 30.0, 30.0, 30.0, 30.0])
        accel = risk_acceleration(scores)
        assert accel == 0.0

    def test_single_score(self) -> None:
        scores = np.array([50.0])
        accel = risk_acceleration(scores)
        assert accel == 0.0


class TestEarlyWarnings:
    def test_critical_score(self) -> None:
        warnings = generate_early_warnings(
            composite_score=85.0,
            risk_acceleration_val=2.0,
            volatility=0.25,
            beta=1.0,
            downside_beta=1.0,
            var_95=0.02,
            avg_correlation=0.5,
        )
        assert any("CRITICAL" in w for w in warnings)

    def test_high_beta_warning(self) -> None:
        warnings = generate_early_warnings(
            composite_score=50.0,
            risk_acceleration_val=0.0,
            volatility=0.20,
            beta=1.8,
            downside_beta=1.8,
            var_95=0.02,
            avg_correlation=0.5,
        )
        assert any("BETA" in w for w in warnings)

    def test_no_warnings_for_safe(self) -> None:
        warnings = generate_early_warnings(
            composite_score=15.0,
            risk_acceleration_val=0.0,
            volatility=0.10,
            beta=0.8,
            downside_beta=0.8,
            var_95=0.01,
            avg_correlation=0.3,
        )
        assert len(warnings) == 0
