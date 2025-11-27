from tests.factories import OrderFactory


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