# Testing Strategy

This section outlines the testing protocols, tools, and structure used in the CryptoFlow project to ensure code quality and reliability.

## Overview
We employ a modular testing strategy focusing on:
-   **Unit Tests**: Verifying individual components in isolation.
-   **Integration Tests**: Verifying interactions between multiple components.
-   **Factories**: Generating dynamic, realistic test data.

## Tools
The following tools are central to our testing ecosystem:

| Tool | Purpose |
|------|---------|
| **pytest** | The primary test runner and framework. |
| **pytest-mock** | For mocking external dependencies (e.g., databases, APIs). |
| **faker** | Generates random, realistic data (names, text, addresses). |
| **factory_boy** | Creates persistent/object-based test data using Faker. |

## Folder Structure
All tests are located in the `tests/` directory at the project root:

```
tests/
├── factories/          # Reusable data factories
│   ├── __init__.py     # Exposes factories
│   ├── ai_factories.py # Factories for AI module
│   └── order_factory.py# Factories for Orders
├── unit_tests/         # Unit tests (isolated)
│   ├── ai/             # AI module unit tests
│   └── ...
└── integration_tests/  # Integration tests (connected)
    ├── ai/             # AI API & Semantic Search integration
    └── test_api_routes.py # API Route integration
```

## Workflow
The testing workflow is designed to be efficient and reproducible.

### Diagram
```mermaid
--8<-- "docs/documentation/diagrams/testing/test_workflow.mmd"
```

## Writing Tests
### 1. Using Factories
Don't hardcode data. Use factories to generate it dynamically.
```python
from tests.factories.ai_factories import DocumentChunkFactory

# Create a single chunk
chunk = DocumentChunkFactory.create_chunk()

# Create a batch
chunks = DocumentChunkFactory.create_batch(size=5)
```

### 2. Mocking Dependencies
Use `pytest-mock` to isolate the code under test.
```python
def test_something(mocker):
    mock_db = mocker.patch("src.db.Database")
    # ... test logic ...
```

## Running Tests
To run all tests:
```bash
# Activate venv
source venv/bin/activate

# Run pytest
pytest
```

To run a specific test file:
```bash
pytest tests/unit_tests/ai/test_knowledge_base.py
```

To run integration tests specifically:
```bash
pytest -m integration
```
