#!/bin/bash
export PYTHONPATH=$(pwd)
echo "Starting CryptoFlow MCP Server (SSE Mode) on port 8000..."
echo "Endpoint: http://localhost:8000/sse"

venv/bin/python3 src/entrypoints/mcp_server.py --transport sse --port 8000
