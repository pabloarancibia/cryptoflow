import math
import random

from abc import ABC, abstractmethod
from typing import List, Literal

# Value Object for the result
SignalType = Literal["BUY", "SELL", "HOLD"]


class TradingStrategy(ABC):
    """
    The Strategy Interface.
    Any algorithm (RSI, MACD, AI model) must implement this.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def calculate_signal(self, prices: List[float]) -> SignalType:
        """
        Analyzes historical prices and returns a signal.
        """
        pass


class MovingAverageStrategy(TradingStrategy):
    """
    Basic Trend Following:
    - BUY if price > SMA (Uptrend)
    - SELL if price < SMA (Downtrend)
    """

    def __init__(self, window: int = 5):
        super().__init__(f"SMA_{window}")
        self.window = window

    def calculate_signal(self, prices: List[float]) -> SignalType:
        if len(prices) < self.window:
            return "HOLD"

        # Calculate SMA of the last N prices
        recent_prices = prices[-self.window:]
        avg_price = sum(recent_prices) / len(recent_prices)
        current_price = prices[-1]

        if current_price > avg_price:
            return "BUY"
        elif current_price < avg_price:
            return "SELL"
        return "HOLD"


class RSIStrategy(TradingStrategy):
    """
    Mean Reversion:
    - BUY if RSI < 30 (Cheap/Oversold)
    - SELL if RSI > 70 (Expensive/Overbought)
    """

    def __init__(self, period: int = 14):
        super().__init__(f"RSI_{period}")
        self.period = period

    def calculate_signal(self, prices: List[float]) -> SignalType:
        if len(prices) < self.period + 1:
            return "HOLD"

        # --- Simplified RSI Logic for HFT Speed ---
        # 1. Calculate price changes
        deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        recent_deltas = deltas[-self.period:]

        # 2. Separate gains and losses
        gains = [d for d in recent_deltas if d > 0]
        losses = [abs(d) for d in recent_deltas if d < 0]

        # 3. Calculate Average Gain/Loss
        avg_gain = sum(gains) / self.period
        avg_loss = sum(losses) / self.period

        if avg_loss == 0:
            return "SELL"  # Infinite RSI -> Overbought

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # 4. Generate Signal
        if rsi < 30:
            return "BUY"
        elif rsi > 70:
            return "SELL"

        return "HOLD"

    # --- CPU BOUND TASK ---
    # This function must be at the top level to be picklable by multiprocessing
def run_monte_carlo_simulation(base_price: float, iterations: int = 5_000_000) -> dict:
    """
    Simulates millions of price paths to calculate Value at Risk (VaR).
    This is a BLOCKING CPU-bound operation.
    """
    results = []
    # Heavy mathematical loop
    for _ in range(iterations):
        # Simulate a random daily return
        shock = random.gauss(0, 1)  # Standard normal distribution
        simulated_price = base_price * math.exp(0.01 + 0.2 * shock)
        results.append(simulated_price)

    # Calculate statistics
    avg_price = sum(results) / len(results)
    min_price = min(results)
    max_price = max(results)

    return {
        "iterations": iterations,
        "average_price": round(avg_price, 2),
        "min_price": round(min_price, 2),
        "max_price": round(max_price, 2)
    }