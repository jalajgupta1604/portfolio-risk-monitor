import numpy as np

from app.risk_engine.stress import run_stress_tests
from app.risk_engine.volatility import compute_log_returns


class TestStressTests:
    def test_three_scenarios(self) -> None:
        rng = np.random.default_rng(42)
        port_ret = rng.normal(0, 0.02, 60)
        bench_ret = rng.normal(0, 0.012, 60)
        results = run_stress_tests(port_ret, bench_ret, 1_000_000.0, beta=1.2)
        assert len(results) == 3

    def test_scenarios_are_negative(self) -> None:
        rng = np.random.default_rng(42)
        port_ret = rng.normal(0, 0.02, 60)
        bench_ret = rng.normal(0, 0.012, 60)
        results = run_stress_tests(port_ret, bench_ret, 1_000_000.0, beta=1.2)
        for r in results:
            assert r.portfolio_impact_pct < 0
            assert r.estimated_loss < 0

    def test_larger_shock_larger_loss(self) -> None:
        rng = np.random.default_rng(42)
        port_ret = rng.normal(0, 0.02, 60)
        bench_ret = rng.normal(0, 0.012, 60)
        results = run_stress_tests(port_ret, bench_ret, 1_000_000.0, beta=1.0)
        losses = [abs(r.estimated_loss) for r in results]
        assert losses == sorted(losses)

    def test_custom_scenarios(self) -> None:
        rng = np.random.default_rng(42)
        port_ret = rng.normal(0, 0.02, 60)
        bench_ret = rng.normal(0, 0.012, 60)
        results = run_stress_tests(
            port_ret, bench_ret, 500_000.0, beta=1.0, scenarios=[-0.10, -0.20]
        )
        assert len(results) == 2
