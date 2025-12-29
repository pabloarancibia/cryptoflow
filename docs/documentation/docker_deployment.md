# Docker Deployment Guide

This guide explains how to build and deploy the CryptoFlow services using the universal Docker image.

## Overview

The project uses a **Universal Docker Image** strategy. A single `Dockerfile` contains all the necessary code and dependencies to run any service in the system (API, Worker, MCP, gRPC). The specific service is selected at runtime using the entrypoint script.

## Building the Image

To build the image, run the following command from the project root:

```bash
docker build -t cryptoflow:latest .
```

This creates a multi-stage, optimized image based on `python:3.11-slim`.

## Running Services

The entrypoint script `scripts/entrypoint.sh` handles service switching based on the first argument provided to the container.

### 1. HTTP API (FastAPI)

This is the default service if no argument is provided.

```bash
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name cryptoflow-api \
  cryptoflow:latest api
```
*Access at: http://localhost:8000/docs*

### 2. Celery Worker

Runs the background task worker.

```bash
docker run -d \
  --env-file .env \
  --name cryptoflow-worker \
  cryptoflow:latest worker
```

### 3. MCP Agent (AI Server)

Runs the Model Context Protocol server (network exposed via SSE).

```bash
docker run -d \
  -p 8001:8000 \
  --env-file .env \
  --name cryptoflow-mcp \
  cryptoflow:latest mcp
```
*Access at: http://localhost:8001/sse* (Note: mapped to host port 8001 to avoid conflict with API)

### 4. Market Data Service (gRPC)

Runs the gRPC server for market data simulation.

```bash
docker run -d \
  -p 50051:50051 \
  --env-file .env \
  --name cryptoflow-grpc \
  cryptoflow:latest grpc
```

## Docker Compose

For local development, use the provided `docker-compose.yml` to orchestrate the full stack:

```bash
docker compose up --build
```

### Services Included
- **Infrastructure**: Postgres, Redis, RabbitMQ, ChromaDB
- **App Services**:
  - `api` (Port 8000)
  - `worker` (Background tasks)
  - `mcp` (AI Agent on Port 8001)
  - `grpc` (Market Data on Port 50051)

This configuration handles all networking, dependency ordering, and environment variables automatically.

## Implementation Details

- **Base Image**: `python:3.11-slim`
- **User**: Runs as non-root `appuser` (UID 1000) for security.
- **Entrypoint**: `/app/scripts/entrypoint.sh`
- **Healthcheck**: Built-in curl check on port 8000 (valid for API and MCP).
