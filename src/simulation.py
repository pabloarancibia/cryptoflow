import cProfile
import pstats
from domain.entities import Order
from domain.market_data import MarketDataReader
from config import MARKET_DATA_CSV


def expensive_strategy_calculation(price):
    """Simulates a heavy CPU-bound math operation."""
    total = 0
    for i in range(10000):
        total += (price * i) ** 0.5
    return total


def run_backtest():
    loader = MarketDataReader(str(MARKET_DATA_CSV))  # Ensure path is string

    print("Starting Backtest...")
    for tick in loader.start_stream():
        price = float(tick['price'])

        signal = expensive_strategy_calculation(price)

        if signal > 100:
            # Order uses __slots__, so this is fast
            order = Order(
                order_id=tick['timestamp'],
                symbol="BTC",
                quantity=1.0,
                price=price,
                side="BUY"
            )

    print("Backtest Complete.")


if __name__ == "__main__":
    cProfile.run('run_backtest()', 'backtest.prof')