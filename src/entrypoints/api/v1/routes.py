from fastapi import APIRouter, Depends, Request, HTTPException
from src.application.dtos import OrderCreate, OrderResponse
from src.application.use_cases.analyze_market import AnalysisRequest, AnalysisResponse, AnalyzeMarketUseCase
from src.application.use_cases.run_backtest import RunBacktestUseCase
from src.infrastructure.grpc_client import grpc_client_manager
from src.generated import order_pb2
from src.infrastructure.adapters.mock_exchange import MockExchangeAdapter
# Removed direct DB dependencies for Order placement
# from src.infrastructure.uow_postgres import SqlAlchemyUnitOfWork

router = APIRouter()

# Dependency Injection Setup
# def get_uow(): ... (Removed for pure Gateway logic on this route, or kept for others if needed)

# Define the Dependency for the Adapter
def get_exchange_client():
    # In Week 4/5, we can swap this for BinanceExchangeAdapter(api_key=...)
    return MockExchangeAdapter()

def get_analyze_market_use_case(
        exchange=Depends(get_exchange_client)
):
    return AnalyzeMarketUseCase(exchange)

def get_backtest_use_case():
    import main
    return RunBacktestUseCase(main.process_pool)


@router.post("/orders", response_model=OrderResponse)
async def place_order(order_data: OrderCreate):
    try:
        stub = grpc_client_manager.get_order_stub()
        
        # Helper: Convert Pydantic -> Protobuf
        req = order_pb2.OrderRequest(
            symbol=order_data.symbol,
            quantity=order_data.quantity,
            price=order_data.price,
            side=order_data.side
        )
        
        # Call gRPC Service
        grpc_res = await stub.PlaceOrder(req)
        
        # Helper: Convert Protobuf -> Pydantic
        return OrderResponse(
            order_id=grpc_res.order_id,
            status=grpc_res.status,
            message=grpc_res.message
        )
    except Exception as e:
        # Map gRPC errors to HTTP exceptions if needed
        raise HTTPException(status_code=500, detail=str(e))

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

@router.post("/backtest")
async def run_backtest(
    price: float = 50000.0,
    use_case: RunBacktestUseCase = Depends(get_backtest_use_case)
):
    """
    Triggers a CPU-Heavy Simulation.
    Because we use Multiprocessing, this should NOT block the Health Check.
    """
    result = await use_case.execute(price)
    return result
