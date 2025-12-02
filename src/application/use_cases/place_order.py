import uuid
import structlog
from src.domain.entities import Order
from src.application.ports.interfaces import AbstractUnitOfWork, ExchangeClient
from src.application.dtos import OrderCreate, OrderResponse
from src.domain.services import SymbolRegistry

logger = structlog.get_logger()

class PlaceOrderUseCase:
    def __init__(self, uow: AbstractUnitOfWork, exchange: ExchangeClient):
        # Dependency Injection: We depend on the Abstract UoW, not a specific DB
        self.uow = uow
        self.exchange = exchange

    async def execute(self, data: OrderCreate) -> OrderResponse:
        """
        1. Open Transaction
        2. Create Domain Entity
        3. Add to Repo
        4. Commit
        """
        logger.info("placing_order", symbol=data.symbol, side=data.side, qty=data.quantity)

        async with self.uow:
            # VALIDATION via Domain Service
            SymbolRegistry.validate(data.symbol)

            # Use the Adapter to get external data
            # We fetch the "Real" market price to store as metadata or validate spread
            market_price = await self.exchange.get_current_price(data.symbol)

            if data.metadata is None:
                data.metadata = {}
            data.metadata["market_price_snapshot"] = market_price

            # Create the Domain Entity (Pure Python)
            # Business Logic: Generate ID here, not in DB
            new_order = Order(
                order_id=str(uuid.uuid4()),
                symbol=data.symbol,
                quantity=data.quantity,
                price=data.price,
                side=data.side,
                metadata=data.metadata
            )

            # Persist using the Repository inside the UoW
            # Note: We use .add(), not .save(). It's not in the DB yet.
            await self.uow.orders.add(new_order)

            # request_id auto-added by middleware
            logger.info("order_created", order_id=new_order.order_id, price=new_order.price)

            # Commit happens automatically on __exit__
            # If line 2 failed, Commit would never happen.

            # Return DTO
            return OrderResponse.model_validate(new_order)