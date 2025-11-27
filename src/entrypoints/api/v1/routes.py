# src/entrypoints/api/v1/routes.py
from fastapi import APIRouter, Depends, HTTPException
from src.application.dtos import OrderCreate, OrderResponse
from src.application.use_cases.place_order import PlaceOrderUseCase
from src.infrastructure.uow import InMemoryUnitOfWork

router = APIRouter()

# 1. Dependency Injection Setup
# In a real app, this might come from a container, but a function works fine.
def get_uow():
    return InMemoryUnitOfWork()

def get_place_order_use_case(uow=Depends(get_uow)):
    return PlaceOrderUseCase(uow)

# 2. The Endpoint
@router.post("/orders", response_model=OrderResponse)
def place_order(
    order_data: OrderCreate,
    use_case: PlaceOrderUseCase = Depends(get_place_order_use_case)
):
    try:
        # The Controller is THIN. It just calls the Use Case.
        return use_case.execute(order_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))