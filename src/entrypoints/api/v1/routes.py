# src/entrypoints/api/v1/routes.py
from fastapi import APIRouter, Depends
from src.application.dtos import OrderCreate, OrderResponse
from src.application.use_cases.place_order import PlaceOrderUseCase
from src.infrastructure.uow import InMemoryUnitOfWork
from src.infrastructure.adapters.mock_exchange import MockExchangeAdapter

router = APIRouter()

# Dependency Injection Setup
# In a real app, this might come from a container, but a function works fine.
def get_uow():
    return InMemoryUnitOfWork()

# Define the Dependency for the Adapter
def get_exchange_client():
    # In Week 4/5, we can swap this for BinanceExchangeAdapter(api_key=...)
    return MockExchangeAdapter()

# Inject both into the Use Case
def get_place_order_use_case(
        uow=Depends(get_uow),
        exchange=Depends(get_exchange_client)
):
    return PlaceOrderUseCase(uow, exchange)

@router.post("/orders", response_model=OrderResponse)
def place_order(
    order_data: OrderCreate,
    use_case: PlaceOrderUseCase = Depends(get_place_order_use_case)
):

    # If logic fails, the Global Handler catches it automatically.
    return use_case.execute(order_data)