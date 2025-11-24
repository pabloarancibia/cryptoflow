import cProfile
import pstats
from src.domain.market_data import MarketDataReader
from src.domain.order import Order
from src.config import MARKET_DATA_CSV


def expensive_strategy_calculation(price):
    """Simulates a heavy CPU-bound math operation (e.g., complex indicator)."""
    total = 0
    # This loop burns CPU cycles holding the GIL
    for i in range(10000):
        total += (price * i) ** 0.5
    return total


def run_backtest():
    loader = MarketDataReader(MARKET_DATA_CSV)

    print("Starting Backtest...")
    for tick in loader.start_stream():
        price = float(tick['price'])

        # CPU Bound part
        signal = expensive_strategy_calculation(price)

        # Object creation part
        if signal > 100:
            order = Order(tick['timestamp'], "BTC", 1.0, price, "BUY")

    print("Backtest Complete.")


if __name__ == "__main__":
    # We use cProfile to measure performance
    # profiler = cProfile.Profile()
    # profiler.enable()
    #
    # run_backtest()
    #
    # profiler.disable()
    # stats = pstats.Stats(profiler).sort_stats('cumtime')
    # stats.print_stats(10)
    cProfile.run('run_backtest()', 'backtest.prof')