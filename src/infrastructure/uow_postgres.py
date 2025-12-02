import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.ports.interfaces import AbstractUnitOfWork
from src.infrastructure.repositories.postgres import SqlAlchemyOrderRepository
from src.infrastructure.database import get_session_factory

logger = structlog.get_logger()

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.session_factory = get_session_factory()
        self.session: AsyncSession = None

    async def __aenter__(self):
        self.session = self.session_factory()
        # Initialize Repositories
        self.orders = SqlAlchemyOrderRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await super().__aexit__(exc_type, exc_val, exc_tb)
        finally:
            # Always close session
            await self.session.close()

    async def commit(self):
        await self.session.commit()
        logger.info("db_commit", db="postgres")

    async def rollback(self):
        await self.session.rollback()
        logger.warning("db_rollback", db="postgres")