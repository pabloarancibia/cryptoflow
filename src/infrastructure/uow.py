import structlog

from src.application.ports.interfaces import AbstractUnitOfWork
from src.infrastructure.repositories.memory import InMemoryOrderRepository

logger = structlog.getLogger()

class InMemoryUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.orders = InMemoryOrderRepository()
        self.committed = False

    def commit(self):
        self.committed = True
        logger.info("uow_commit", db="memory", status="flushed")

    def rollback(self):
        self.committed = False
        logger.warning("uow_rollback", db="memory")