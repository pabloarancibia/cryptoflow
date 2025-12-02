from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from src.domain.entities import Order
from src.infrastructure.models import OrderModel
from src.application.ports.interfaces import OrderRepository

class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, order: Order) -> None:
        """
        Maps Domain Entity -> DB Model -> Session Add
        """
        model = OrderModel(
            order_id=order.order_id,
            symbol=order.symbol,
            quantity=order.quantity,
            price=order.price,
            side=order.side,
            metadata=order.metadata
        )
        self.session.add(model)

    async def get_by_id(self, order_id: str) -> Optional[Order]:
        """
        Fetches from DB Model -> Maps to Domain Entity
        """
        query = select(OrderModel).where(OrderModel.order_id == order_id)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if model is None:
                return None

        return Order(
            order_id=model.order_id,
            symbol=model.symbol,
            quantity=model.quantity,
            price=model.price,
            side=model.side,
            metadata=model.meta_data
        )