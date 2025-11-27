from tests.factories import OrderFactory
import pytest
from src.domain.services import SymbolRegistry
from src.domain.exceptions import InvalidSymbolError


def test_deep_copy_independence():
    """Use Factory to generate a complex order, then test copying."""

    # 1. Create random order
    original = OrderFactory.build_entity(metadata={"strategy": "RSI"})

    # 2. Deep Clone
    clone = original.deep_clone()

    # 3. Modify Clone
    clone.metadata["strategy"] = "MACD"

    # 4. Assert Original is safe
    assert original.metadata["strategy"] == "RSI"
    # Also verify random values match initially
    assert original.price == clone.price
    assert original.symbol == clone.symbol


def test_order_slots_memory():
    """Verify random orders adhere to __slots__."""
    order = OrderFactory.build_entity()

    try:
        order.random_attribute = "Should Fail"
        assert False, "Should have raised AttributeError"
    except AttributeError:
        assert True


def test_symbol_registry_validation():
    """Test that the Registry correctly allows/blocks symbols."""

    # 1. Happy Path (Supported)
    try:
        SymbolRegistry.validate("BTC")
        SymbolRegistry.validate("usd")  # Should handle lowercase
    except InvalidSymbolError:
        pytest.fail("Registry rejected valid symbols!")

    # 2. Error Path (Unsupported)
    with pytest.raises(InvalidSymbolError) as exc_info:
        SymbolRegistry.validate("ZZZZ")

    assert "not supported" in str(exc_info.value)