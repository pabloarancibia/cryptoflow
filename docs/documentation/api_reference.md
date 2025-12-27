# API Reference

Complete API endpoint documentation for CryptoFlow Trading Engine.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production, implement JWT or OAuth2 authentication.

## Endpoints

### Health Check

Check if the API is running.

**Endpoint:** `GET /`

**Response:**
```json
{
  "status": "active",
  "system": "CryptoFlow"
}
```

---

### Place Order

Place a new trading order through the gRPC Order Service.

**Endpoint:** `POST /api/v1/orders`

**Request Body:**
```json
{
  "symbol": "BTCUSDT",
  "quantity": 0.1,
  "price": 50000.0,
  "side": "BUY",
  "metadata": {
    "strategy": "SMA_5",
    "notes": "Moving average crossover signal"
  }
}
```

**Request Schema:**
- `symbol` (string, required): Trading pair symbol (e.g., "BTCUSDT")
- `quantity` (float, required): Order quantity
- `price` (float, required): Order price
- `side` (string, required): Order side - "BUY" or "SELL"
- `metadata` (object, optional): Additional order metadata

**Response:**
```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PENDING",
  "symbol": "BTCUSDT",
  "quantity": 0.1,
  "price": 50000.0,
  "side": "BUY",
  "metadata": {
    "strategy": "SMA_5",
    "notes": "Moving average crossover signal"
  }
}
```

**Response Schema:**
- `order_id` (string): Unique order identifier
- `status` (string): Order status (PENDING, FILLED, CANCELLED, REJECTED)
- `symbol` (string): Trading pair symbol
- `quantity` (float): Order quantity
- `price` (float): Order price
- `side` (string): Order side
- `metadata` (object): Order metadata

**Error Responses:**

- `500 Internal Server Error`: gRPC service unavailable or error occurred
  ```json
  {
    "detail": "Error message description"
  }
  ```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "quantity": 0.1,
    "price": 50000.0,
    "side": "BUY"
  }'
```

---

### Analyze Market

Analyze market data using a specified trading strategy.

**Endpoint:** `POST /api/v1/analyze`

**Request Body:**
```json
{
  "symbol": "BTCUSDT",
  "strategy": "SMA",
  "window": 5,
  "prices": [48000, 48500, 49000, 49500, 50000]
}
```

**Request Schema:**
- `symbol` (string, required): Trading pair symbol
- `strategy` (string, required): Strategy name - "SMA" or "RSI"
- `window` (integer, optional): Window size for strategy (default: 5 for SMA, 14 for RSI)
- `prices` (array of floats, required): Historical price data

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "strategy": "SMA_5",
  "signal": "BUY",
  "confidence": 0.75,
  "analysis": {
    "current_price": 50000.0,
    "moving_average": 49000.0,
    "trend": "UPTREND"
  }
}
```

**Response Schema:**
- `symbol` (string): Trading pair symbol
- `strategy` (string): Strategy name used
- `signal` (string): Trading signal - "BUY", "SELL", or "HOLD"
- `confidence` (float): Signal confidence (0.0 to 1.0)
- `analysis` (object): Strategy-specific analysis data

**Available Strategies:**

1. **SMA (Simple Moving Average)**
   - `window`: Number of periods (default: 5)
   - Signal logic:
     - BUY: Current price > SMA
     - SELL: Current price < SMA
     - HOLD: Insufficient data or price ≈ SMA

2. **RSI (Relative Strength Index)**
   - `window`: Number of periods (default: 14)
   - Signal logic:
     - BUY: RSI < 30 (oversold)
     - SELL: RSI > 70 (overbought)
     - HOLD: 30 ≤ RSI ≤ 70

**Error Responses:**

- `400 Bad Request`: Invalid request parameters
  ```json
  {
    "detail": "Invalid strategy name. Available: SMA, RSI"
  }
  ```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "strategy": "SMA",
    "window": 5,
    "prices": [48000, 48500, 49000, 49500, 50000]
  }'
```

---

### Run Backtest

Execute a CPU-intensive backtest simulation. Uses multiprocessing to avoid blocking the main API.

**Endpoint:** `POST /api/v1/backtest`

**Query Parameters:**
- `price` (float, optional): Starting price for backtest (default: 50000.0)

**Response:**
```json
{
  "status": "completed",
  "iterations": 1000000,
  "duration_seconds": 2.45,
  "result": {
    "final_price": 50123.45,
    "profit_loss": 123.45
  }
}
```

**Response Schema:**
- `status` (string): Backtest status
- `iterations` (integer): Number of simulation iterations
- `duration_seconds` (float): Execution time in seconds
- `result` (object): Backtest results

**Note:** This endpoint uses multiprocessing to offload CPU-intensive work, ensuring the API remains responsive.

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/backtest?price=50000.0"
```

---

## Error Handling

All endpoints follow consistent error handling:

### Standard Error Response

```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Endpoint or resource not found
- `500 Internal Server Error`: Server error or service unavailable

### Domain Exceptions

Domain-specific exceptions are automatically converted to appropriate HTTP responses:

- `DomainError`: Converted to `400 Bad Request` or `500 Internal Server Error` based on context
- `InvalidSymbolError`: Converted to `400 Bad Request`
- `InsufficientFundsError`: Converted to `400 Bad Request`

---

## Rate Limiting

Currently, no rate limiting is implemented. In production, consider implementing:

- Per-IP rate limiting
- Per-user rate limiting (with authentication)
- Endpoint-specific rate limits

---

## API Versioning

The API uses URL-based versioning:

- Current version: `v1` (`/api/v1/...`)
- Future versions: `v2`, `v3`, etc.

When breaking changes are introduced, a new version will be created while maintaining backward compatibility for previous versions.

---

## Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces allow you to:
- Explore all available endpoints
- Test API calls directly from the browser
- View request/response schemas
- See example requests and responses

---

## gRPC Services

Some functionality is provided via gRPC services:

- **Market Data Service**: Real-time market data streaming
- **Order Service**: Order placement and management

See [gRPC Implementation Guide](grpc_implementation_guide.md) for details on using gRPC services directly.

