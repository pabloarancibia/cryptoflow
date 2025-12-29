from contextlib import asynccontextmanager
from concurrent.futures import ProcessPoolExecutor
from fastapi import FastAPI
from src.entrypoints.api.v1.routes import router as v1_router
from src.domain.exceptions import DomainError
from src.entrypoints.api.errors import domain_exception_handler
from src.application.factories import StrategyFactory
from src.domain.strategies import MovingAverageStrategy, RSIStrategy
from src.infrastructure.logging import configure_logging
from src.entrypoints.api.middleware import RequestLogMiddleware

# Setup Logging
configure_logging()

# Register Strategies
StrategyFactory.register("SMA", MovingAverageStrategy)
StrategyFactory.register("RSI", RSIStrategy)


# --- GLOBAL STATE ---
# We store the pool here so routes can access it
process_pool: ProcessPoolExecutor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: Create the process pool
    # max_workers=None defaults to the number of CPU cores on your machine
    global process_pool
    print("--- STARTING PROCESS POOL ---")
    process_pool = ProcessPoolExecutor()

    # STARTUP: Initialize gRPC Client Manager
    from src.infrastructure.grpc_client import grpc_client_manager
    await grpc_client_manager.initialize()

    yield

    # SHUTDOWN: Clean up resources
    print("--- SHUTTING DOWN PROCESS POOL ---")
    process_pool.shutdown()

    # SHUTDOWN: Close gRPC connections
    await grpc_client_manager.close()

app = FastAPI(
    title="CryptoFlow HFT Engine",
    description="High-Frequency Trading Simulation with Clean Architecture",
    version="1.0.0",
    lifespan=lifespan  # Register the lifespan handler
)

app.add_middleware(RequestLogMiddleware)
app.add_exception_handler(DomainError, domain_exception_handler)
app.include_router(v1_router, prefix="/api/v1", tags=["Trading"])


@app.get("/")
def health_check():
    return {"status": "active", "system": "CryptoFlow"}