# Project History: Weeks 1-7 (Architecture Evolution)

This document serves as a retroactive summary of the architectural decisions, core concepts, and system evolution of **CryptoFlow** from inception to Week 7.

---

## 1. Core Concepts (Weeks 1-2)

The foundation of CryptoFlow is built upon strict Python principles to ensure performance and maintainability in a High-Frequency Trading (HFT) context.

### Global Interpreter Lock (GIL)
*   **Concept**: A mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecodes at once.
*   **HFT Relevance**: Pure Python threads cannot parallelize CPU-bound tasks (like heavy strategy indicators).
*   **Our Solution**: We use **AsyncIO** for I/O-bound tasks (Market Data ingestion, Order routing) and plan to use **Multiprocessing** for CPU-bound Strategy Engine calculations to bypass the GIL.

### Memory Model & Optimization
*   **Concept**: Python's dynamic typing involves significant memory overhead.
*   **Application**: We implemented `__slots__` in our core `Order` entity.
    *   **Result**: Reduced memory footprint per object by preventing the creation of `__dict__`.
    *   **Trade-off**: Inflexibility (cannot add attributes at runtime), which is acceptable for strict domain entities.

### Context Managers & Transactional Safety
*   **Concept**: The `with` statement (`__enter__`, `__exit__`) ensures resources are managed correctly.
*   **Application**: Our `UnitOfWork` (UoW) implements the Context Manager protocol.
    *   **Benefit**: Automatic rollback of database transactions if an error occurs during order processing.
    *   **Code**: `async with uow: ...` ensures atomicity.

---

## 2. Architecture Overview (Week 3)

By Week 3, we transitioned from an in-memory prototype to a robust **Layered Architecture** with persistent storage.

### Component Diagram (Current State)

```mermaid
--8<-- "docs/documentation/diagrams/architecture/architecture_component.mmd"
```

### Layer Definitions
1.  **Entrypoints**: Handles HTTP requests, validation (Pydantic), and routing. Zero business logic.
2.  **Application**: Orchestrates use cases (e.g., `PlaceOrder`). Coordinates UoW, Repositories, and Event Publishers.
3.  **Domain**: Pure business logic (Entities, Value Objects). Zero external dependencies.
4.  **Infrastructure**: Technical implementations (SQLAlchemy, AioPika, Redis).

---

## 3. Key Technical Decisions (Weeks 3-4)

### Pydantic V2
*   **Decision**: strict usage of Pydantic V2 for Data Transfer Objects (DTOs).
*   **Why**: V2 is written in Rust and offers significant performance improvements (serialization speed) over V1, critical for API latency.
*   **Usage**: `OrderCreate`, `OrderResponse` models enforce type safety at the edge.

### Dependency Injection (DI)
*   **Decision**: Use FastAPI's `Depends` system to inject services and UoW.
*   **Why**: Decoupling. It allows us to easily swap `SqlAlchemyUnitOfWork` with `InMemoryUnitOfWork` for unit tests without changing application logic.
*   **Implementation**: `get_uow` dependency provider.

### Repository Pattern
*   **Decision**: Abstract database access behind a `Repository` interface.
*   **Why**: Separation of Concerns. The Domain layer should not know we are using PostgreSQL. It only knows it can `save()` an order.
*   **Benefit**: easier testing and future migration (e.g., to a time-series DB) if needed.

### Async Pipelines (Week 4 Focus)
*   **Decision**: adoption of `asyncio` for the Market Data Fetcher.
*   **Scenario**: Fetching prices for 50 tickers.
*   **Optimization**: Instead of sequential requests (50 * Latency), we use `asyncio.gather()` to fire all requests simultaneously.
*   **Impact**: drastically reduced latency for the "Get Market Data" operation.

---

## 4. Week 5: Containerization (DevOps)
*   **Goal**: Create a reproducible environment.
*   **Action**: Fully Dockerized the application using `docker-compose`.
*   **Services**:
    *   `web`: FastAPI Application.
    *   `db`: PostgreSQL.
    *   `redis`: Caching & Locking.
    *   `rabbitmq`: Event Broker.
*   **Outcome**: "It works on my machine" is solved. One command (`docker-compose up`) starts the entire stack.

---

## 5. Week 6: Microservices & gRPC (Scaling)
*   **Transition**: Moved from Monolith to Microservices for critical components.
*   **Change**: Extracted `OrderService` and `MarketDataService` into standalone gRPC processes.
*   **Protocol**: Replaced internal function calls with efficient **gRPC (Protobuf)** calls.
*   **Why**:
    *   **Latency**: gRPC is much faster than REST for internal comms.
    *   **Independence**: `MarketDataService` can now crash without taking down the Order Entry system.

---

## 6. Week 7: AI & Agentic Workflows (Innovation)
*   **Goal**: Enable natural language interaction with the trading engine.
*   **Implementation**:
    *   **RAG (Retrieval-Augmented Generation)**: Ingested `docs/` folder into a specialized Knowledge Base for asking "How does X work?" questions.
    *   **Agentic Tool Use**: Implemented a "Trader Agent" that parses natural language ("Buy 10 ETH") and executes trades by calling the `PlaceOrderUseCase`.
*   **Bridge**: Created a sync-to-async bridge to allow the synchronous Agent loop to drive the fully asynchronous Application Layer.

---

## 7. Future Roadmap
*   **K8s**: Full Kubernetes deployment.
*   **LLM Upgrade**: Replace Heuristic Agent with GPT-4o.
*   **Monitoring**: Prometheus & Grafana dashboards.
