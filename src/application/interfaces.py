# src/application/interfaces.py
from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities import Order

# 1. The Repository Port
# The Use Case says: "I need a place to store Orders. I don't care if it's SQL or RAM."
class OrderRepository(ABC):
    @abstractmethod
    def add(self, order: Order) -> None:
        """Mark an order to be saved."""
        pass

    @abstractmethod
    def get_by_id(self, order_id: str) -> Optional[Order]:
        pass

# 2. The Unit of Work Port
# The Use Case says: "I need a transaction boundary."
class AbstractUnitOfWork(ABC):
    orders: OrderRepository  # The UoW provides access to the Repos

    def __enter__(self) -> 'AbstractUnitOfWork':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    @abstractmethod
    def commit(self):
        """Flush changes to persistence."""
        pass

    @abstractmethod
    def rollback(self):
        """Revert changes."""
        pass