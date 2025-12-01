from pydantic import BaseModel
from src.application.interfaces import ExchangeClient
from src.application.factories import StrategyFactory

# DTOs for this specific Use Case
class AnalysisRequest(BaseModel):
    symbol: str
    strategy: str # e.g. "RSI"
    parameters: dict = {}

class AnalysisResponse(BaseModel):
    symbol: str
    signal: str # "BUY", "SELL", "HOLD"
    current_price: float

class AnalyzeMarketUseCase:
    def __init__(self, exchange: ExchangeClient):
        self.exchange = exchange

    async def execute(self, request: AnalysisRequest) -> AnalysisResponse:
        # 1. Fetch History (Adapter)
        # We need enough data for the strategy (e.g., 20 candles)
        history = await self.exchange.get_price_history(request.symbol, limit=20)
        current_price = history[-1]

        # 2. Instantiate Strategy (Factory)
        strategy = StrategyFactory.create(request.strategy, request.parameters)

        # 3. Run Logic (Strategy Pattern)
        signal = strategy.calculate_signal(history)

        return AnalysisResponse(
            symbol=request.symbol,
            signal=signal,
            current_price=current_price
        )