from sqlalchemy import String, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from src.infrastructure.database import Base


class OrderModel(Base):
    """
    SQLAlchemy Table Definition.
    Maps the 'orders' table in PostgreSQL.
    """
    __tablename__ = "orders"

    # Primary Key
    order_id: Mapped[str] = mapped_column(String, primary_key=True)

    # Core Fields
    symbol: Mapped[str] = mapped_column(String, index=True)  # Indexed for fast lookup
    quantity: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float)
    side: Mapped[str] = mapped_column(String(4))  # "BUY" or "SELL"
    status: Mapped[str] = mapped_column(String, default="NEW")

    # JSONB field for flexible metadata
    # In Postgres, this is highly efficient
    meta_data: Mapped[dict] = mapped_column("metadata", JSON, default={})

    def __repr__(self):
        return f"<OrderDB(id={self.order_id}, sym={self.symbol})>"