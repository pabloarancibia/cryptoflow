# src/domain/entities.py
from abc import ABC, abstractmethod
from typing import ClassVar, Optional, Dict, Any
import copy

# --- 1. FINANCIAL INSTRUMENTS (Polymorphic Assets) ---

class FinancialInstrument(ABC):
    """Abstract Base Class for all tradable assets."""
    instrument_type: ClassVar[str] = "GENERIC"

    def __init__(self, symbol: str):
        self.symbol = symbol.upper()
        if not self.validate_symbol():
            raise ValueError(f"Invalid symbol format: {self.symbol}")

    @abstractmethod
    def validate_symbol(self) -> bool:
        pass

    @abstractmethod
    def calculate_valuation(self, amount: float, current_price: float) -> float:
        pass

    @abstractmethod
    def quantize(self, amount: float) -> float:
        """Round the amount to the asset's specific precision."""
        pass

    @abstractmethod
    def calculate_fee(self, quantity: float, price: float) -> float:
        pass

    def __repr__(self):
        return f"<{self.instrument_type}: {self.symbol}>"


class CryptoAsset(FinancialInstrument):
    instrument_type = "CRYPTO"
    PRECISION = 8
    FEE_RATE = 0.001  # 0.1%

    def validate_symbol(self) -> bool:
        return 3 <= len(self.symbol) <= 5

    def calculate_valuation(self, amount: float, current_price: float) -> float:
        return amount * current_price

    def quantize(self, amount: float) -> float:
        return round(amount, self.PRECISION)

    def calculate_fee(self, quantity: float, price: float) -> float:
        return (quantity * price) * self.FEE_RATE


class FiatCurrency(FinancialInstrument):
    instrument_type = "FIAT"
    PRECISION = 2
    FLAT_FEE = 1.00

    def validate_symbol(self) -> bool:
        return len(self.symbol) == 3

    def calculate_valuation(self, amount: float, current_price: float) -> float:
        return amount * current_price

    def quantize(self, amount: float) -> float:
        return round(amount, self.PRECISION)

    def calculate_fee(self, quantity: float, price: float) -> float:
        return self.FLAT_FEE


# --- 2. ORDER ENTITY (Memory Optimized) ---

class Order:
    """
    Represents a buy/sell order.
    Uses __slots__ for memory optimization in HFT scenarios.
    """
    __slots__ = ['order_id', 'symbol', 'quantity', 'price', 'side', 'status', 'metadata']

    def __init__(self,
                 order_id: str,
                 symbol: str,
                 quantity: float,
                 price: float,
                 side: str,
                 metadata: Optional[Dict[str, Any]] = None):
        self.order_id = order_id
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.side = side
        self.status = "PENDING"
        self.metadata = metadata if metadata is not None else {}


    def shallow_clone(self):
        return copy.copy(self)

    def deep_clone(self):
        return copy.deepcopy(self)

    def __repr__(self):
        return f"Order({self.order_id}, {self.symbol}, {self.side}, {self.quantity} @ {self.price})"

    def __eq__(self, other):
        if not isinstance(other, Order):
            return NotImplemented
        return self.order_id == other.order_id

    def __hash__(self):
        return hash(self.order_id)