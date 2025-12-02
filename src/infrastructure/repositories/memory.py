from typing import Dict, Optional
from src.domain.entities import Order
from src.application.ports.interfaces import OrderRepository

class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self._storage: Dict[str, Order] = {}

    def add(self, order: Order) -> None:
        self._storage[order.order_id] = order

    def get_by_id(self, order_id: str) -> Optional[Order]:
        return self._storage.get(order_id)