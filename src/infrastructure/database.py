from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from src.config import DATABASE_URL

# Create Async Engine
# echo=True prints raw SQL to stdout (great for learning/debugging)
engine = create_async_engine(DATABASE_URL, echo=False)

# Session Factory
# This generates new sessions for each request
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Base Class for ORM Models
# All DB tables will inherit from this
class Base(DeclarativeBase):
    pass

# Helper for direct access (if needed outside UoW)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session