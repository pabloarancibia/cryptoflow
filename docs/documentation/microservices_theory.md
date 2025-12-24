# Microservices with gRPC: Theory & Concepts

## 1. Monolith vs. Microservices

### Monolithic Architecture
In a **Monolithic** architecture (like the initial state of CryptoFlow), all components (Market Data, Order Processing, Portfolio) reside in a single codebase and process.

-   **Pros**: Simple to develop, deploy, and debug initially.
-   **Cons**:
    -   **Scalability**: You must scale the entire application, even if only one module (e.g., Market Data) needs more resources.
    -   **Coupling**: Tight coupling between components makes refactoring risky.
    -   **Resilience**: A crash in one part (e.g., a memory leak in analytics) can bring down the entire system.

### Microservices Architecture
In **Microservices**, the application is broken down into small, independent services communicating over a network.

-   **Pros**:
    -   **Independent Scaling**: Scale the Market Data service on high-CPU machines and the Order service on high-memory machines.
    -   **Fault Isolation**: If the Market Data service crashes, the Order service can still accept orders.
    -   **Tech Freedom**: Write one service in Python and another in Go or Rust.

### Visual Comparison

```mermaid
--8<-- "docs/documentation/diagrams/architecture/monolith_vs_microservices.mmd"
```

---

## 2. What is gRPC?

**gRPC** (Google Remote Procedure Call) is a high-performance framework for communication between services.

Status Quo (REST/JSON):
-   Uses HTTP/1.1 (text-based).
-   Payloads are JSON (human-readable but large/slow to parse).
-   Unidirectional (Client -> Server -> Response).

**gRPC**:
-   Uses **HTTP/2**: Supports multiplexing and header compression.
-   **Binary Serialization**: Uses Protocol Buffers (Protobuf) instead of JSON.
-   **Streaming**: Native support for bi-directional streaming.

---

## 3. Protocol Buffers (Protobuf)

Protobuf is the Interface Definition Language (IDL) for gRPC.

### Why Protobuf?
1.  **Strict Typing**: Fields have strict types (`int32`, `string`, `float`).
2.  **Performance**:
    -   **Smaller Size**: Field names are replaced by numbered tags, saving massive bandwidth.
    -   **Faster Parsing**: Parsing binary data is orders of magnitude faster than parsing text JSON.

### The `.proto` file
The contract between client and server.
```protobuf
// Definition
message OrderRequest {
  string symbol = 1;
  double quantity = 2; // "2" is the unique tag for this field
}
```

---

## 4. Relevance to High-Frequency Trading (HFT)

In HFT, **latency is everything**.
-   **REST/JSON latency**: ~50ms - 200ms (Unacceptable)
-   **gRPC latency**: < 10ms (Often sub-millisecond on internal networks)

Using gRPC ensures that our `MarketDataService` can push price updates to the `OrderService` or `StrategyEngine` with minimal delay.

---

## 5. Concrete Implementation: Authentication Service

To start our transition to Microservices, we are extracting the **Authentication** logic.

### Why separate Auth?
Authentication is a high-traffic, low-compute operation. Every single request hits it. By separating it:
1.  **Security**: User credentials are isolated in their own database.
2.  **Performance**: We can run 10 replicas of the Auth Service to handle login storms without affecting the Trading Engine.

### Interaction Flow

When a user logs in, the Main API (Gateway) talks to the Auth Service.

```mermaid
--8<-- "docs/documentation/diagrams/flows/auth_service_flow.mmd"
```
