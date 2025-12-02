from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from src.config import DATABASE_URL

# --- LAZY LOADING ---
_engine = None
_session_factory = None

def get_engine():
    """Create engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(DATABASE_URL, echo=False)
    return _engine

def get_session_factory():
    """Create session factory using the engine lazy."""
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )
    return _session_factory

# Base Class for ORM Models
# All DB tables will inherit from this
class Base(DeclarativeBase):
    pass

# Helper for direct access (if needed outside UoW)
async def get_db():
    SessionLocal = get_session_factory()
    async with SessionLocal() as session:
        yield session