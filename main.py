from fastapi import FastAPI
from src.entrypoints.api.v1.routes import router as v1_router
from src.domain.exceptions import DomainError
from src.entrypoints.api.errors import domain_exception_handler
app = FastAPI(
    title="CryptoFlow HFT Engine",
    description="High-Frequency Trading Simulation with Clean Architecture",
    version="1.0.0"
)

# Global Exception Handler
# catches ANY DomainError raised anywhere in the app
app.add_exception_handler(DomainError, domain_exception_handler)

# Mount the routers
app.include_router(v1_router, prefix="/api/v1", tags=["Trading"])

@app.get("/")
def health_check():
    return {"status": "active", "system": "CryptoFlow"}