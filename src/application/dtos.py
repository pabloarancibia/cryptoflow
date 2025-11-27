# src/application/dtos.py
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any

# 1. Base Schema (Shared fields)
class OrderBase(BaseModel):
    symbol: str = Field(..., min_length=3, max_length=5, description="Asset Symbol (e.g. BTC)")
    quantity: float = Field(..., description="Amount to trade")
    price: float = Field(..., description="Limit price")
    side: str = Field(..., description="BUY or SELL")

# 2. Input Schema (DTO for POST /orders)
class OrderCreate(OrderBase):
    # Optional metadata user might send
    metadata: Optional[Dict[str, Any]] = None

    @field_validator('quantity', 'price')
    @classmethod
    def check_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Must be positive value')
        return v

    @field_validator('side')
    @classmethod
    def check_side(cls, v: str) -> str:
        s = v.upper()
        if s not in ('BUY', 'SELL'):
            raise ValueError('Side must be BUY or SELL')
        return s

# 3. Output Schema (DTO for returning data)
class OrderResponse(OrderBase):
    order_id: str
    status: str
    metadata: Dict[str, Any]

    # Pydantic V2 Config:
    # 'from_attributes=True' allows Pydantic to read data from
    # your custom class (Order) attributes, not just dicts.
    model_config = ConfigDict(from_attributes=True)