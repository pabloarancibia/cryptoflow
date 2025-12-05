from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from src.domain.entities import Order

# 1. The Repository Port
# The Use Case says: "I need a place to store Orders. I don't care if it's SQL or RAM."
class OrderRepository(ABC):
    @abstractmethod
    async def add(self, order: Order) -> None:
        """Mark an order to be saved."""
        pass

    @abstractmethod
    async def get_by_id(self, order_id: str) -> Optional[Order]:
        pass

# 2. The Unit of Work Port
# The Use Case says: "I need a transaction boundary."
class AbstractUnitOfWork(ABC):
    orders: OrderRepository  # The UoW provides access to the Repos

    async def __aenter__(self) -> 'AbstractUnitOfWork':
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()

    @abstractmethod
    async def commit(self):
        """Flush changes to persistence."""
        pass

    @abstractmethod
    async def rollback(self):
        """Revert changes."""
        pass


# --- Exchange Adapter Port ---
class ExchangeClient(ABC):
    """
    Interface for interacting with external crypto exchanges.
    Clean Architecture: The Application layer defines this, Infrastructure implements it.
    """

    @abstractmethod
    async def get_current_price(self, symbol: str) -> float:
        """Fetch real-time price for a symbol."""
        pass

    @abstractmethod
    async def get_latest_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Fetch multiple prices in parallel.
        Returns: {"BTC": 50000.0, "ETH": 3000.0}
        """
        pass

    @abstractmethod
    async def get_price_history(self, symbol: str, limit: int = 20) -> List[float]:
        """Fetch historical close prices for analysis."""
        pass