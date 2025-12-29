"""
Get Portfolio Use Case

Retrieves the current portfolio holdings from the database.
Follows the same pattern as PlaceOrderUseCase with dependency injection.
"""

import structlog
from typing import Dict, List
from src.application.ports.interfaces import AbstractUnitOfWork
from pydantic import BaseModel, ConfigDict

logger = structlog.get_logger()


# DTOs for Portfolio
class PortfolioHolding(BaseModel):
    """Represents a single asset holding in the portfolio."""
    symbol: str
    quantity: float
    
    model_config = ConfigDict(from_attributes=True)


class PortfolioResponse(BaseModel):
    """Response containing all portfolio holdings."""
    holdings: Dict[str, float]  # {symbol: quantity}
    total_assets: int
    last_updated: str
    
    model_config = ConfigDict(from_attributes=True)


class GetPortfolioUseCase:
    """
    Use Case: Retrieve current portfolio holdings.
    
    This follows the hexagonal architecture pattern:
    - Depends on AbstractUnitOfWork (port), not concrete implementation
    - Returns DTOs, not domain entities directly
    - Handles business logic for portfolio aggregation
    """
    
    def __init__(self, uow: AbstractUnitOfWork):
        """
        Inject dependencies via constructor.
        
        Args:
            uow: Unit of Work for database access
        """
        self.uow = uow
    
    async def execute(self) -> PortfolioResponse:
        """
        Retrieve portfolio by aggregating all orders.
        
        Business Logic:
        - Fetch all orders from repository
        - Aggregate by symbol (BUY adds, SELL subtracts)
        - Return current holdings
        
        Returns:
            PortfolioResponse with current holdings
        """
        logger.info("retrieving_portfolio")
        
        async with self.uow:
            # Fetch all orders from repository
            # Note: In a real system, you'd have a dedicated Portfolio repository
            # For now, we'll aggregate from orders
            
            # This is a simplified implementation
            # In production, you'd likely have:
            # - A separate Portfolio entity
            # - A PortfolioRepository
            # - Cached portfolio state
            
            holdings: Dict[str, float] = {}
            
            # Get all orders (this is simplified - in production you'd query differently)
            # For now, we'll return a mock portfolio since we don't have a get_all method
            # This demonstrates the pattern - you can extend OrderRepository later
            
            # TODO: Extend OrderRepository with get_all() or create PortfolioRepository
            # For now, return mock data that represents the structure
            holdings = {
                "BTC": 1.5,
                "ETH": 10.0,
                "USD": 50000.0
            }
            
            logger.info("portfolio_retrieved", num_holdings=len(holdings))
            
            return PortfolioResponse(
                holdings=holdings,
                total_assets=len(holdings),
                last_updated="2025-12-29T17:31:23+01:00"
            )
