# Azure AI Integration (Phase 4)

This document details the integration of **Microsoft Azure AI** services into the CryptoFlow AI module. This "Enterprise Layer" implementation introduces **Microsoft Semantic Kernel** for LLM orchestration and **Azure AI Search** for advanced hybrid vector retrieval.

## Overview

The Azure integration is designed to coexist with existing ChromaDB and OpenAI/Google implementations, strictly following the **Hexagonal Architecture** (Ports & Adapters) pattern. This ensures that the core application remains agnostic to the underlying infrastructure while leveraging Azure's enterprise-grade capabilities.

## Architecture

The integration adds two new adapters to the Infrastructure layer:

1.  **Azure Semantic Kernel Adapter**: Implements `ILLMProvider` using Microsoft Semantic Kernel.
2.  **Azure Search Adapter**: Implements `IVectorStore` using Azure AI Search.

### Architecture Diagram

```mermaid
  --8<-- "docs/documentation/diagrams/architecture/azure_integration_class_diagram.mmd"
```

---

## Semantic Kernel Adapter

Located in [`src/ai/adapters/azure/llm_adapter.py`](file:///home/ecom/Codes/cryptoflow/src/ai/adapters/azure/llm_adapter.py).

We use **Microsoft Semantic Kernel (SK)** v1.x as the orchestration framework for Azure OpenAI. SK provides a robust plugin system and automatic function calling capabilities.

### Key Features

*   **Logic Separation**: Tools are registered as **Plugins**, keeping prompt logic separate from execution logic.
*   **Automatic Function Calling**: The adapter uses `FunctionChoiceBehavior.Auto` to let the model intelligently select tools.
*   **Dynamic Registration**: The adapter dynamically converts the project's generic tool definitions (dict) into SK functions at runtime, utilizing the `@kernel_function` decorator pattern.

### Code Example: Dynamic Tool Registration

```python
def _register_tools_as_plugin(self, tools: List[Dict], plugin_name: str) -> None:
    # Dynamic creation of SK functions from dictionary definitions
    for tool in tools:
        @kernel_function(name=tool["name"], description=tool["description"])
        def tool_func(**kwargs) -> str:
            return json.dumps(kwargs)
        
        # Register with Kernel
        self.kernel.add_function(plugin_name=plugin_name, function=tool_func)
```

---

## Azure AI Search Adapter

Located in [`src/ai/adapters/azure/search_adapter.py`](file:///home/ecom/Codes/cryptoflow/src/ai/adapters/azure/search_adapter.py).

This adapter implements the `IVectorStore` interface using **Azure AI Search**. Unlike simple vector stores, it uses **Hybrid Search** (Vector + Keyword) for superior retrieval quality.

### Features

*   **Auto-Index Creation**: Automatically provisions the search index with the correct schema (Vector, ID, Content, Source) if it doesn't exist.
*   **Hybrid Retrieval**: Combines:
    *   **Vector Search**: For semantic meaning (using `all-MiniLM-L6-v2` embeddings).
    *   **Keyword Search**: BM25 for exact matches.
*   **Metadata Handling**: Preserves document metadata for source tracking.

### Configuration

The index is configured with `HnswAlgorithmConfiguration` for efficient vector search performance.

---

## Configuration & Factory

The system automatically detects Azure credentials and prioritizes Azure adapters via the Factory pattern.

### Environment Variables

To enable the Azure stack, set the following variables in your `.env` file:

```bash
# === Azure OpenAI (Semantic Kernel) ===
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# === Azure AI Search ===
AZURE_SEARCH_ENDPOINT=https://your-resource.search.windows.net
AZURE_SEARCH_API_KEY=your_search_key
AZURE_SEARCH_INDEX_NAME=cryptoflow-docs
```

### Factory Priority

1.  **LLM**: `LLMFactory` checks `AZURE_OPENAI_ENDPOINT` first. If present, it returns `AzureSemanticKernelAdapter`.
2.  **Vector Store**: `VectorStoreFactory` checks `AZURE_SEARCH_ENDPOINT`. If present, it returns `AzureSearchAdapter`; otherwise, it falls back to `ChromaDB`.

---

## Testing

Comprehensive tests ensure the Azure integration works correctly.

### Unit Tests
Run the mocked unit tests (no Azure connection required):
```bash
python3 tests/unit_tests/test_azure_adapters.py
```

### Integration Tests
Run end-to-end tests (requires Azure credentials):
```bash
python3 tests/integration_tests/test_azure_integration.py
```
