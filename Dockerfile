# Universal Dockerfile for CryptoFlow
# Supports: API, Worker, MCP Agent, gRPC Services

# ==========================================
# Stage 1: Builder
# ==========================================
FROM python:3.11-slim as builder

# Install system dependencies for build
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create virtual environment
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
# hadolint ignore=DL3013
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================
# Stage 2: Runtime
# ==========================================
FROM python:3.11-slim

# Install runtime system dependencies
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Copy source code and config
COPY --chown=appuser:appuser src /app/src
COPY --chown=appuser:appuser main.py /app/main.py
COPY --chown=appuser:appuser scripts /app/scripts
COPY --chown=appuser:appuser alembic.ini /app/alembic.ini

# Set correct permissions
RUN chmod +x /app/scripts/entrypoint.sh

# Switch to non-root user
USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default Entrypoint
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD []
