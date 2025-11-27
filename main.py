from fastapi import FastAPI
from src.entrypoints.api.v1.routes import router as v1_router

app = FastAPI(
    title="CryptoFlow HFT Engine",
    description="High-Frequency Trading Simulation with Clean Architecture",
    version="1.0.0"
)

# Mount the routers
app.include_router(v1_router, prefix="/api/v1", tags=["Trading"])

@app.get("/")
def health_check():
    return {"status": "active", "system": "CryptoFlow"}