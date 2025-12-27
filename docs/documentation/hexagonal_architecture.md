# Hexagonal Architecture (Ports & Adapters)

The AI module (`src/ai`) has been refactored to follow **Hexagonal Architecture**. This ensures the core business logic is isolated from external details like databases, APIs, and frameworks.

## 1. Core Principles

-   **Dependency Rule**: Source code dependencies only point inward.
-   **Isolation**: The domain layer knows nothing about the database or the web framework.
-   **Testability**: Can test business logic without spinning up real databases or external APIs.

## 2. Directory Structure

The structure mimics the architectural layers:

```bash
src/ai/
├── domain/           # The Core (Inner Hexagon)
│   ├── models.py     # Pure Python data structures
│   └── ports.py      # Abstract Interfaces (Ports)
├── application/      # Use Cases (Orchestration)
│   ├── rag_service.py
│   └── agent_service.py
├── adapters/         # Infrastructure (Outer Hexagon)
│   ├── chroma_adapter.py
│   ├── llm/          # LLM Package
│   │   ├── base.py
│   │   ├── google.py
│   │   ├── openai.py
│   │   └── factory.py
│   └── trading_tools_adapter.py
└── main.py           # Composition Root (Wiring)
```

## 3. Layers Breakdown

### Domain Layer (The Center)
Contains the "Truth" of the application.
-   **Models**: `DocumentChunk`, `AgentResponse`. Simple dataclasses.
-   **Ports**: `IVectorStore`, `ILLMProvider`. Abstract Base Classes (ABCs) defining *what* the application needs, not *how* it's done.

### Application Layer (The Orchestrator)
Contains the specific rules and workflows.
-   **Services**: `RAGService`, `TraderAgent`.
-   **Logic**: Injects Ports via `__init__`. Calls methods on Ports to get work done. Does not import from `adapters`.

### Adapters Layer (The Infrastructure)
Implementations of the Ports.
-   **ChromaKBAdapter**: Uses `chromadb` library.
-   **LLMAdapter**: Replaced by `adapters.llm` package with `GoogleGenAIAdapter` and `OpenAIAdapter`.
-   **TradingToolAdapter**: Connects to the broader system.

## 4. Architecture Diagram

```mermaid
--8<-- "docs/documentation/diagrams/architecture/hexagonal_layers.mmd"
```

## 5. Wiring (Dependency Injection)

We use a "Composition Root" pattern in `src/ai/main.py` to wire everything together at startup.

```python
# Create Adapters (Infrastructure)
db = ChromaKBAdapter()
llm = LLMFactory.create_provider()

# Inject into Services (Application)
rag = RAGService(vector_store=db, llm_provider=llm)
```
