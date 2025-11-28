from fastapi import FastAPI
from src.entrypoints.api.v1.routes import router as v1_router
from src.domain.exceptions import DomainError
from src.entrypoints.api.errors import domain_exception_handler
from src.application.factories import StrategyFactory
from src.domain.strategies import MovingAverageStrategy, RSIStrategy

from src.infrastructure.logging import configure_logging
from src.entrypoints.api.middleware import RequestLogMiddleware
from src.application.factories import StrategyFactory
from src.domain.strategies import MovingAverageStrategy, RSIStrategy

# Setup Logging
configure_logging()

# Register Strategies
StrategyFactory.register("SMA", MovingAverageStrategy)
StrategyFactory.register("RSI", RSIStrategy)


app = FastAPI(
    title="CryptoFlow HFT Engine",
    description="High-Frequency Trading Simulation with Clean Architecture",
    version="1.0.0"
)

app.add_middleware(RequestLogMiddleware)

# Global Exception Handler
# catches ANY DomainError raised anywhere in the app
app.add_exception_handler(DomainError, domain_exception_handler)

# Mount the routers
app.include_router(v1_router, prefix="/api/v1", tags=["Trading"])

@app.get("/")
def health_check():
    return {"status": "active", "system": "CryptoFlow"}