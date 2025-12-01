from fastapi import APIRouter, Depends
from src.application.dtos import OrderCreate, OrderResponse
from src.application.use_cases.place_order import PlaceOrderUseCase
from src.application.use_cases.analyze_market import AnalysisRequest, AnalysisResponse, AnalyzeMarketUseCase
from src.infrastructure.uow import InMemoryUnitOfWork
from src.infrastructure.adapters.mock_exchange import MockExchangeAdapter
from src.infrastructure.uow_postgres import SqlAlchemyUnitOfWork

router = APIRouter()

# Dependency Injection Setup
def get_uow():
    return SqlAlchemyUnitOfWork()

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

def get_analyze_market_use_case(
        exchange=Depends(get_exchange_client)
):
    return AnalyzeMarketUseCase(exchange)

@router.post("/orders", response_model=OrderResponse)
async def place_order(
    order_data: OrderCreate,
    use_case: PlaceOrderUseCase = Depends(get_place_order_use_case)
):

    # If logic fails, the Global Handler catches it automatically.
    return await use_case.execute(order_data)

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_market(
    request: AnalysisRequest,
    use_case: AnalyzeMarketUseCase = Depends(get_analyze_market_use_case)
):
    """
    Dynamic Analysis Endpoint.
    User chooses the strategy at runtime!
    """
    return await use_case.execute(request)