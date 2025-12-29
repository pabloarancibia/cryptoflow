import asyncio
import time
import sys
from pathlib import Path

# project root
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.infrastructure.adapters.mock_exchange import MockExchangeAdapter


async def run_benchmark():
    adapter = MockExchangeAdapter()
    symbols = ["BTC", "ETH", "SOL", "ADA", "DOT", "XRP", "LTC", "DOGE", "AVAX", "MATIC"]

    print(f"--- Benchmarking Fetch for {len(symbols)} Symbols ---")
    print("Simulated Latency per call: 0.2s\n")

    # ensure hit the sleep() latency
    print("Clearing cache...")
    for sym in symbols:
        await adapter.cache.set(f"price:{sym}", "", ttl=1)
    await asyncio.sleep(0.1)

    # 1. Sequential (The Slow Way)
    print("1. Running Sequential...")
    start_seq = time.time()
    for sym in symbols:
        await adapter.get_current_price(sym)
    duration_seq = time.time() - start_seq
    print(f"   -> Time Taken: {duration_seq:.4f} seconds")

    # Clear cache
    print("Clearing cache...")
    for sym in symbols:
        await adapter.cache.set(f"price:{sym}", "", ttl=1)
    await asyncio.sleep(0.1)

    # 2. Concurrent
    print("2. Running Concurrent (asyncio.gather)...")
    start_conc = time.time()
    await adapter.get_latest_prices(symbols)
    duration_conc = time.time() - start_conc
    print(f"   -> Time Taken: {duration_conc:.4f} seconds")

    # Summary
    if duration_conc > 0:
        speedup = duration_seq / duration_conc
        print(f"\n Speedup Factor: {speedup:.2f}x faster")

    # Close Redis connection cleanly
    await adapter.cache.close()


if __name__ == "__main__":
    asyncio.run(run_benchmark())