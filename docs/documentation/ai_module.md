# CryptoFlow AI Module: Architecture & Implementation Guide

**Date:** December 24, 2025  
**Module:** `src/ai`  
**Status:** Beta (v0.2)  
**Authors:** CryptoFlow Engineering Team

---

## 1. Executive Summary
This document details the implementation of the AI & Vector Sprint. The goal was to evolve CryptoFlow from a purely programmatic HFT engine into an **Agentic System** capable of understanding natural language commands and retrieving technical context from documentation.

This implementation introduces two core capabilities:
1.  **Retrieval-Augmented Generation (RAG):** A local knowledge base that indexes project documentation for semantic search.
2.  **Agentic Workflow:** A "Trader Agent" that translates natural language intent into structured database transactions using the **Tool Use** pattern.

---

## 2. High-Level Architecture
The AI module sits as an **Interface Layer** on top of the existing Clean Architecture. It does not replace the Domain or Application layers; rather, it acts as a new client (alongside the REST API and gRPC services) that consumes them.

### System Context Diagram
```mermaid
--8<-- "docs/documentation/diagrams/ai/ai_system_context.mmd"
```

---

## 3. Component 1: The Knowledge Base (RAG)
The Knowledge Base is responsible for answering questions about the system's internal workings. It implements a **Sparse Vector Retrieval** mechanism using `BM25` (Best Matching 25), simulating the behavior of a Vector Database like ChromaDB.

### 3.1 Data Pipeline
The ingestion pipeline transforms unstructured Markdown files into queryable chunks.
1.  **Discovery:** Recursively scans `docs/**/*.md`.
2.  **Chunking:** Splits text based on double newlines (`\n\n`) to preserve paragraph context. Headers are kept with their associated text where possible.
3.  **Indexing:** Tokenizes text and builds an inverted index using `rank_bm25`.

### 3.2 Retrieval Process
When a query is received (e.g., "How does the Repository Pattern work?"):
1.  The query is tokenized.
2.  The engine calculates a relevance score for every chunk in the index.
3.  The top N (default 3) chunks are returned to the user or Agent context.

### RAG Flow Diagram
```mermaid
--8<-- "docs/documentation/diagrams/ai/ai_rag_flow.mmd"
```

---

## 4. Component 2: The Trader Agent
The Trader Agent utilizes the **ReAct (Reason + Act)** pattern to interact with the system. It bridges the gap between unstructured English and structured Python objects.

### 4.1 Intent Parsing (The "Brain")
Now powered by **Native Function Calling** (LLM Tool Use).
*   **Provider:** Google Vertex AI (Gemini 2.0) or OpenAI (GPT-4o).
*   **Mechanism:** The LLM receives a list of available tools (e.g., `execute_trade`) in its context window. It autonomously decides whether to call a tool or reply with text based on the user's prompt.
*   **Parsers:** No manual regex parsing. The SDK returns structured `ToolCall` objects.

### 4.2 Tool Use (The "Hands")
The Agent is isolated from the backend. It interacts only through defined Tools.

**Tool Name:** `execute_trade`  
**Signature:** `(symbol: str, side: str, quantity: float)`  

**Responsibility:**
1.  Receives clean parameters from the Agent.
2.  Validates inputs.
3.  **Bridges Sync to Async:** Uses `asyncio.run()` to invoke the asynchronous `PlaceOrderUseCase`.
4.  Returns a JSON-serializable output (Order ID or Error Message).

### Agent Execution Logic
```mermaid
--8<-- "docs/documentation/diagrams/ai/ai_agent_logic.mmd"
```

---

## 5. Implementation Details & Code Structure

### Directory Map
```bash
src/ai/
├── domain/           # Models & Ports
├── adapters/         # Infrastructure (LLM, Store, Tools)
│   ├── llm/          # LLM Providers (Google, OpenAI)
│   └── ...
├── application/      # RAG & Agent Services
│   ├── tools/        # Tool Definitions
│   └── ...
└── main.py           # Composition Root
```

### Key Technical Challenge: The Async Bridge
Since the Agent runs in a synchronous loop (standard for simple CLI tools) but the Core CryptoFlow Engine is fully asynchronous (SQLAlchemy/FastAPI), the tool must handle the Event Loop management.

**Code Snippet (The Bridge):**
```python
# Inside src/ai/trader_agent.py

def execute_trade(symbol, side, quantity):
    async def run_backend_logic():
        # ... dependencies initialization ...
        response = await use_case.execute(order_dto)
        return response

    # The Sync-to-Async Bridge
    result = asyncio.run(run_backend_logic()) 
    return result.order_id
```

---

## 6. Future Improvements (Roadmap to Production)
To move this from a prototype (v0.1) to a production-grade AI system (v1.0), the following upgrades are required:

1.  **Upgrade "Brain":** [COMPLETED] Migrated to Google/OpenAI Native Function Calling.
2.  **Upgrade "Memory":** Replace BM25 in `knowledge_base.py` with **ChromaDB** or **Pinecone**.
    *   *Mechanism:* Use `sentence-transformers` to generate dense vector embeddings (Float32 arrays) for better semantic understanding (e.g., understanding that "digital gold" likely refers to "BTC").
3.  **Guardrails:** Implement a "Risk Management" layer before the tool executes. The AI should not be allowed to place orders larger than a specific value without a secondary confirmation step.
