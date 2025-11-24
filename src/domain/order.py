import copy
from typing import Optional, Dict, Any

class Order:
    # OPTIMIZATION: __slots__ restricts attribute creation to these specific fields
    # This eliminates the overhead of a dynamic __dict__ per object.
    __slots__ = ['order_id', 'symbol', 'quantity', 'price', 'side', 'metadata']
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
        # Dangerous if we just do self.metadata = metadata and metadata is mutable
        self.metadata = metadata if metadata is not None else {}

    def shallow_clone(self):
        """Fast, but metadata dict is shared between copies."""
        return copy.copy(self)

    def deep_clone(self):
        """Slower, but safe. Metadata is fully independent."""
        return copy.deepcopy(self)

    def __repr__(self):
        return f"Order({self.order_id}, {self.symbol}, meta={self.metadata})"