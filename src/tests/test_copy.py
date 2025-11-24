import pytest
from src.domain.order import Order


@pytest.fixture
def sample_order():
    return Order("101", "BTCUSD", 1.5, 60000.0, "BUY", {"strategy": "RSI"})


def test_shallow_copy_risk(sample_order):
    """Verify that shallow copy shares metadata (The 'Danger')"""
    shallow = sample_order.shallow_clone()

    shallow.metadata["strategy"] = "MACD"

    # Assert that original changed too (proving it is shallow)
    assert sample_order.metadata["strategy"] == "MACD"


def test_deep_copy_safety(sample_order):
    """Verify that deep copy protects the original"""
    # Reset data
    sample_order.metadata["strategy"] = "RSI"

    deep = sample_order.deep_clone()
    deep.metadata["strategy"] = "Bollinger"

    # Assert original did NOT change
    assert sample_order.metadata["strategy"] == "RSI"
    assert deep.metadata["strategy"] == "Bollinger"