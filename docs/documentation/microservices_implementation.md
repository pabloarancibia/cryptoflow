# Microservices Implementation Guide

This guide details the technical implementation of our two core services: **Market Data** and **Order Processing**.

---

## 1. Market Data Service
**Pattern**: gRPC Server streaming
**Responsibility**: Delivering real-time price updates to clients/strategies.

### Implementation Details
*   **Protocol**: gRPC (HTTP/2)
*   **Method**: `StreamPrices` (Server-side Streaming)
*   **Data Source**: Connects to the Exchange Adapter (which reads from Redis/Mock).

### Workflow
The client opens a connection and requests a specific symbol. The server keeps the channel open and yields chunks of price data as they become available.

```mermaid
--8<-- "docs/documentation/diagrams/flows/market_data_flow.mmd"
```

### Key Python Components
*   `MarketDataService` class: Implements the generated protobuf servicer.
*   `async def StreamPrices`: An asynchronous generator that `yield`s `PriceUpdate` messages.

---

## 2. Order Processing Service
**Pattern**: Unary gRPC + Transactional DB
**Responsibility**: Validating, persisting, and routing orders.

### Implementation Details
*   **Protocol**: gRPC (Unary - Request/Response)
*   **Method**: `CreateOrder`
*   **Storage**: PostgreSQL (via SQLAlchemy Async)
*   **Messaging**: RabbitMQ (via AioPika)

### Workflow
Unlike market data, this is a transactional operation. ACIDs properties must be guaranteed.

```mermaid
--8<-- "docs/documentation/diagrams/flows/order_processing_flow.mmd"
```

### Key Python Components
*   `OrderService` class: Validates input DTOs.
*   `UnitOfWork`: Manages the database transaction context.
*   `OrderRepository`: Handles SQL `INSERT` statements.
*   `RabbitMQPublisher`: Publishes the `order_created` event after the DB commit.
