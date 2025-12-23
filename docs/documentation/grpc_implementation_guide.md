# gRPC Microservices Implementation Guide

## 1. Theory & Concepts

### Microservices Architecture
This implementation transitions `CryptoFlow` from a monolithic structure to a distinct set of services.
-   **Old World**: All logic in one process. Shared memory.
-   **New World**: Logic split across processes. Network communication.

### gRPC (Google Remote Procedure Call)
A modern open-source high-performance RPC framework that can run in any environment. It can efficiently connect services in and across data centers with pluggable support for load balancing, tracing, health checking and authentication.

#### Key Features:
1.  **Protocol Buffers (Protobuf)**: A powerful binary serialization toolset and language definition format.
    -   **Strict Typing**: Messages are defined with strict types (`int32`, `string`, `float`), reducing compatibility errors.
    -   **Efficiency**: Binary data is much smaller and faster to parse than text-based JSON.
2.  **HTTP/2 Transport**:
    -   **Multiplexing**: Send multiple requests in parallel over a single TCP connection.
    -   **Streaming**: Native bidirectional streaming support.

---

## 2. Technical Implementation Details

### Server Streaming (Market Data)
The **Market Data Service** uses a **Server Streaming RPC** pattern.
-   **Use Case**: Real-time ticker updates. Client subscribes once, receives continuous updates.
-   **Proto Definition**:
    ```protobuf
    rpc StreamMarketData (MarketDataRequest) returns (stream MarketDataResponse) {}
    ```
-   **Python Implementation**:
    We use a Python `generator` (a function with `yield`) to implement the stream. Each yielded object is serialized to a Protobuf binary frame and flushed to the network.

### Unary RPC (Order Processing)
The **Order Service** uses a **Unary RPC** pattern.
-   **Use Case**: Transactional operations. Client sends a request, waits for a single response.
-   **Proto Definition**:
    ```protobuf
    rpc PlaceOrder (OrderRequest) returns (OrderResponse) {}
    ```
-   **Python Implementation**:
    A standard function that returns a single `OrderResponse` object.

### Concurrency Model
The gRPC Python server uses a `ThreadPoolExecutor`.
```python
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
```
-   **Explanation**: Each incoming request is assigned to a thread from the pool.
-   **Implication**: The service can handle 10 concurrent requests. For I/O bound tasks (DB calls), this is efficient. For CPU bound tasks, Python's GIL might be a bottleneck, requirng multiple processes.

### Channel Management
On the client side, we use `grpc.insecure_channel`.
-   **Lifecycle**: Channels are expensive to create (TCP handshake, connection pooling). They should be created once and reused across the application's lifetime, typically as a singleton.

---

## 3. Protocol Buffer Definitions via `protoc`

We generate Python code from our `.proto` files using `grpc_tools.protoc`.
-   `market_data_pb2.py`: Contains the message classes (`MarketDataRequest`).
-   `market_data_pb2_grpc.py`: Contains the server interface (`MarketDataServiceServicer`) and client stub (`MarketDataServiceStub`).

This generation step effectively "compiles" the interface, ensuring that both client and server adhere to the exact same contract.
