# src/infrastructure/uow.py
from src.application.interfaces import AbstractUnitOfWork
from src.infrastructure.repositories.memory import InMemoryOrderRepository

class InMemoryUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.orders = InMemoryOrderRepository()
        self.committed = False

    def commit(self):
        self.committed = True
        print("--- [InMemoryDB] COMMIT: Data flushed ---")

    def rollback(self):
        self.committed = False
        print("--- [InMemoryDB] ROLLBACK ---")