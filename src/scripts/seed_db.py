# src/scripts/seed_db.py
import asyncio
import random
import uuid
import sys
from pathlib import Path

# Add project root to path so we can import src
sys.path.append(str(Path(__file__).resolve().parents[2]))

# FIXED IMPORTS: Use the getters from your lazy-loading database.py
from src.infrastructure.database import get_engine, get_session_factory
from src.infrastructure.models import OrderModel, Base

SYMBOLS = ["BTC", "ETH", "SOL", "ADA", "XRP", "DOT", "DOGE", "AVAX"]
SIDES = ["BUY", "SELL"]


async def seed_data(n=100000):
    print(f"--- Seeding {n} orders ---")

    # 1. Get the Engine instance
    engine = get_engine()

    # 2. Create tables (Idempotent - only creates if missing)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 3. Get the Session Factory
    SessionLocal = get_session_factory()

    async with SessionLocal() as session:
        batch = []
        for i in range(n):
            order = OrderModel(
                order_id=str(uuid.uuid4()),
                symbol=random.choice(SYMBOLS),
                quantity=round(random.uniform(0.1, 10.0), 4),
                price=round(random.uniform(10.0, 60000.0), 2),
                side=random.choice(SIDES),
                status="CLOSED",
                meta_data={"source": "seeder"}
            )
            batch.append(order)

            # Commit in chunks of 1000 to keep memory low
            if len(batch) >= 1000:
                session.add_all(batch)
                await session.commit()
                batch = []
                # Simple progress indicator
                if (i + 1) % 10000 == 0:
                    print(f"Inserted {i + 1} rows...")

        # Commit remaining
        if batch:
            session.add_all(batch)
            await session.commit()

    print(f"\nSuccessfully inserted {n} rows.")


if __name__ == "__main__":
    asyncio.run(seed_data())