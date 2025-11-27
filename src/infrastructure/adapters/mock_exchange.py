import random
from src.application.interfaces import ExchangeClient


class MockExchangeAdapter(ExchangeClient):
    """
    Simulates an external exchange (Binance/Coinbase).
    """

    def get_current_price(self, symbol: str) -> float:
        # Simulate network latency? time.sleep(0.1)

        # Return a consistent-ish fake price based on symbol length to not be totally random
        # or just random for chaos. Let's do random ranges.

        base_prices = {
            "BTC": 60000.0,
            "ETH": 3000.0,
            "SOL": 150.0,
            "USD": 1.0
        }

        base = base_prices.get(symbol.upper(), 10.0)
        # Add some noise (+- 1%)
        noise = random.uniform(-0.01, 0.01)
        return round(base * (1 + noise), 2)