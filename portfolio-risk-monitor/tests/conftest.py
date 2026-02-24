import numpy as np
import pytest
from numpy.typing import NDArray


@pytest.fixture
def sample_prices() -> NDArray[np.float64]:
    rng = np.random.default_rng(42)
    base = 100.0
    returns = rng.normal(0.0005, 0.02, 60)
    return base * np.exp(np.cumsum(returns))


@pytest.fixture
def benchmark_prices() -> NDArray[np.float64]:
    rng = np.random.default_rng(99)
    base = 22000.0
    returns = rng.normal(0.0003, 0.012, 60)
    return base * np.exp(np.cumsum(returns))


@pytest.fixture
def multi_asset_prices() -> NDArray[np.float64]:
    rng = np.random.default_rng(42)
    n_days = 60
    n_assets = 3
    base_prices = np.array([100.0, 200.0, 150.0])
    returns = rng.normal(0.0005, 0.02, (n_days, n_assets))
    return base_prices * np.exp(np.cumsum(returns, axis=0))


@pytest.fixture
def equal_weights() -> NDArray[np.float64]:
    return np.array([1.0 / 3, 1.0 / 3, 1.0 / 3])
