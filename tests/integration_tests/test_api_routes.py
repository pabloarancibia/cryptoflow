from fastapi.testclient import TestClient
from main import app
from tests.factories import OrderFactory

client = TestClient(app)


def test_create_order_happy_path():
    """Test a single random order creation."""
    # 1. Generate random valid payload
    payload = OrderFactory.build_api_payload(symbol="BTC")

    # 2. Send Request
    response = client.post("/api/v1/orders", json=payload)

    # 3. Verify
    assert response.status_code == 200
    data = response.json()

    # Check that response matches our random input
    assert data["symbol"] == "BTC"
    assert data["price"] == payload["price"]
    assert data["status"] == "PENDING"
    assert "order_id" in data


def test_bulk_order_creation():
    """Stress test with 5 random orders."""
    for _ in range(5):
        payload = OrderFactory.build_api_payload()  # Totally random
        response = client.post("/api/v1/orders", json=payload)
        assert response.status_code == 200
