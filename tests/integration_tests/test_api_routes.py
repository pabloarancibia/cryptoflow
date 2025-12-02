import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from tests.factories import OrderFactory

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_order_happy_path(client):
    """Test a single random order creation."""
    # 1. Generate random valid payload
    payload = OrderFactory.build_api_payload(symbol="BTC")

    # 2. Send Request
    response = await client.post("/api/v1/orders", json=payload)

    # 3. Verify
    assert response.status_code == 200
    data = response.json()

    # Check that response matches our random input
    assert data["symbol"] == "BTC"
    assert data["price"] == payload["price"]
    assert data["status"] == "PENDING"
    assert "order_id" in data

@pytest.mark.asyncio
async def test_bulk_order_creation(client):
    """Stress test with 5 random orders."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for _ in range(5):
            payload = OrderFactory.build_api_payload()
            response = await ac.post("/api/v1/orders", json=payload)
            assert response.status_code == 200
