import asyncio
from sqlalchemy import text
from src.infrastructure.database import engine

async def check_connection():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 'Hello from Postgres'"))
            print(result.scalar())
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_connection())