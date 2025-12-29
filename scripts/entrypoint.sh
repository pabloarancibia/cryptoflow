#!/bin/bash
set -e

# Activate virtual environment
. /app/venv/bin/activate

# Service Switcher
case "$1" in
  api)
    echo "Starting FastAPI (HTTP API)..."
    exec uvicorn main:app --host 0.0.0.0 --port 8000
    ;;
  worker)
    echo "Starting Celery Worker..."
    exec celery -A src.infrastructure.celery_app worker --loglevel=info
    ;;
  mcp)
    echo "Starting MCP Server (AI Agent)..."
    # Runs in SSE mode by default for Docker networking
    exec python src/entrypoints/mcp_server.py --transport sse --host 0.0.0.0 --port 8000
    ;;
  grpc)
    echo "Starting gRPC Service (Market Data)..."
    exec python src/services/market_data_service/server.py
    ;;
  *)
    echo "No service specified. Defaulting to FastAPI..."
    exec uvicorn main:app --host 0.0.0.0 --port 8000
    ;;
esac
