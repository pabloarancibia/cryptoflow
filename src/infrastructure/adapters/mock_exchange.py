import asyncio
import random
import json
from typing import List
from src.infrastructure.cache import RedisClient
from src.application.ports.interfaces import ExchangeClient


class MockExchangeAdapter(ExchangeClient):
    """
    Simulates an external exchange (Binance/Coinbase).
    """

    def __init__(self):
        self.cache = RedisClient.get_instance()

    async def get_current_price(self, symbol: str) -> float:
        cache_key = f"price:{symbol.upper()}"

        # Check cache first
        cached_price = await self.cache.get(cache_key)
        if cached_price:
            return float(cached_price)

        # Simulate network latency (Cache Miss)
        await asyncio.sleep(1.02) # Simulate 1.200ms latency

        # Generate random price
        base_prices = {"BTC": 60000.0, "ETH": 3000.0, "SOL": 150.0, "USD": 1.0}
        base = base_prices.get(symbol.upper(), 10.0)
        noise = random.uniform(-0.01, 0.01)
        price = round(base * (1 + noise), 2)

        # Store in cache for next time
        await self.cache.set(cache_key, str(price), ttl=5)

        return price

    async def get_price_history(self, symbol: str, limit: int = 20) -> List[float]:
        """Generates a fake price history trend."""
        base_price = 50000.0
        history = []

        # Walk random steps to create a realistic-looking chart
        current = base_price
        for _ in range(limit):
            change = random.uniform(-50, 50)  # Random walk
            current += change
            history.append(round(current, 2))

        return history