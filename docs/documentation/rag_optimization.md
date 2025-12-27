# RAG Optimization (Phase 2): HyDE & Provider Agnosticism

This section details the **Phase 2** upgrades to the AI Knowledge Base, focusing on retrieval optimization and architectural flexibility.

## 1. Hypothetical Document Embeddings (HyDE)

Standard RAG (Retrieval Augmented Generation) often fails when the user's query doesn't lexically match the document content. **HyDE** solves this by using an LLM to "hallucinate" a hypothetical answer, and then using *that* answer to search the vector database.

### The Process
1.  **Query**: User asks "How does the matching engine work?"
2.  **Hallucination**: LLM generates a fake technical paragraph about the matching engine.
3.  **Embedding**: We vector-embed the *hallucination*, which captures the semantic *shape* of the answer we are looking for.
4.  **Retrieval**: We search ChromaDB for real documents that are semantically close to this hallucination.

This significantly improves retrieval accuracy for abstract or domain-specific queries.

## 2. Architecture: Strategy Pattern

To avoid vendor lock-in, we refactored the AI module to use the **Strategy Pattern**. The system abstractly defines an `LLMProvider` and dynamically selects the concrete implementation at runtime.

### Class Structure

-   **`LLMProvider` (ABC)**: The abstract interface defining `generate_text()`.
-   **`GoogleGeminiProvider`**: Concrete implementation using `google-genai` SDK.
-   **`OpenAIProvider`**: Concrete implementation using `openai` SDK.
-   **`LLMFactory`**: Logic to inspect environment variables and instantiate the correct provider.

### Workflow Diagram

```mermaid
--8<-- "docs/documentation/diagrams/ai/rag_hyde_flow.mmd"
```

## 3. Configuration & Providers

The system is fully controlled via environmental variables in `.env`.

### Priority Logic
The `LLMFactory` checks keys in this order:
1.  **Google Gemini** (`GOOGLE_API_KEY`): **Recommended**. High performance, generous free tier.
2.  **OpenAI** (`OPENAI_API_KEY`): Fallback or alternative preference.

### Switching Providers

To switch capabilities, simply update your `.env` file:

**For Google Gemini:**
```bash
GOOGLE_API_KEY=AIzaSy...
# OPENAI_API_KEY=  <-- Commented out or ignored if Google key is present
```

**For OpenAI:**
```bash
# GOOGLE_API_KEY=  <-- Must be unset or empty
OPENAI_API_KEY=sk-...
```

## 4. Dependencies
-   `google-genai`: Latest Google AI SDK.
-   `openai`: OpenAI Python Client.
-   `python-dotenv`: For secure configuration management.
