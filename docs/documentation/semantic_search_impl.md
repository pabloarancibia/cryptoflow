# Semantic Search Implementation

This page documents the implementation of the Semantic Search feature in the AI module, replacing the previous BM25 keyword matching system.

## Overview

The new system uses **ChromaDB** as a Vector Database and **SentenceTransformers** for generating embeddings. This allows the AI agent to understand the *meaning* (semantics) of a user's query rather than just matching specific words.

## Architecture

### Components

1.  **ChromaDB**: A lightweight, open-source vector database. It runs as a separate service in Docker.
2.  **SentenceTransformers**: A Python framework for state-of-the-art sentence, text and image embeddings. We use the `all-MiniLM-L6-v2` model for its balance of speed and quality.
3.  **KnowledgeBase**: The Python class (`src/ai/knowledge_base.py`) that acts as the interface between the application and ChromaDB.

### workflows

#### 1. Ingestion Workflow
When `ingest_docs()` is called, the system reads all markdown files, chunks them, generates embeddings, and saves them to ChromaDB.

```mermaid
--8<-- "docs/documentation/diagrams/ai/semantic_search_ingestion.mmd"
```

#### 2. Query Workflow
When a user asks a question, the system embeds the query and searches ChromaDB for the most similar chunks.

```mermaid
--8<-- "docs/documentation/diagrams/ai/semantic_search_query.mmd"
```

## Configuration

The implementation relies on the following configuration:

### Docker
The `chroma` service is defined in `docker-compose.yml`:
```yaml
chroma:
  image: chromadb/chroma:latest
  ports:
    - "8000:8000"
  volumes:
    - chroma_data:/chroma/chroma
  environment:
    - IS_PERSISTENT=TRUE
```

### Python Dependencies
Required packages in `requirements.txt`:
- `chromadb`
- `sentence-transformers`

## Usage

See the [AI Module](../ai_module.md) page for general usage instructions.
