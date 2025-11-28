from src.domain.strategies import MovingAverageStrategy, RSIStrategy


def test_sma_strategy_uptrend():
    """Test that SMA says BUY when price jumps up."""
    strategy = MovingAverageStrategy(window=3)

    # Prices increasing: 10, 11, 12. Average is 11.
    # Next price 15 > 11 -> Should BUY
    prices = [10.0, 11.0, 12.0, 15.0]

    signal = strategy.calculate_signal(prices)
    assert signal == "BUY"


def test_sma_strategy_downtrend():
    """Test that SMA says SELL when price crashes."""
    strategy = MovingAverageStrategy(window=3)

    # Average is 20. Current is 10. -> SELL
    prices = [20.0, 20.0, 20.0, 10.0]

    signal = strategy.calculate_signal(prices)
    assert signal == "SELL"


def test_rsi_oversold():
    """Test RSI detects cheap assets (< 30)."""
    strategy = RSIStrategy(period=5)

    # A generic sequence representing a crash (loss, loss, loss)
    # This math setup will result in low RSI
    prices = [100.0, 90.0, 80.0, 70.0, 60.0, 50.0]

    # Depending on exact math, this big drop should trigger BUY
    signal = strategy.calculate_signal(prices)
    assert signal == "BUY"