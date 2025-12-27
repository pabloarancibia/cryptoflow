# Environment Variables Guide

Complete guide to configuring CryptoFlow using environment variables.

## Overview

CryptoFlow uses environment variables for configuration. You can set them in:

1. **`.env` file** (recommended for local development)
2. **System environment variables**
3. **Docker Compose** (for containerized deployments)

## Configuration File

Create a `.env` file in the project root:

```bash
# Copy the example (if available)
cp .env.example .env

# Or create manually
touch .env
```

## Required Variables

### Database Configuration

```bash
# PostgreSQL connection string
# Format: postgresql+asyncpg://user:password@host:port/database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/cryptoflow
```

**Default:** `postgresql+asyncpg://user:password@localhost:5432/cryptoflow`

**Description:** Full connection string for PostgreSQL database using asyncpg driver.

---

## Optional Variables

### Redis Configuration

```bash
# Redis connection URL
REDIS_URL=redis://localhost:6379/0
```

**Default:** `redis://localhost:6379/0`

**Description:** Redis connection URL for caching and distributed locking.

**Used by:**
- `src.infrastructure.cache`
- `src.application.tasks`

---

### Celery Configuration

```bash
# Celery broker URL (RabbitMQ or Redis)
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//

# Celery result backend
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

**Defaults:**
- `CELERY_BROKER_URL`: `amqp://guest:guest@localhost:5672//`
- `CELERY_RESULT_BACKEND`: `redis://localhost:6379/0`

**Description:**
- `CELERY_BROKER_URL`: Message broker for task queue (RabbitMQ recommended)
- `CELERY_RESULT_BACKEND`: Backend for storing task results

**Used by:** `src.infrastructure.celery_app`

---

### RabbitMQ Configuration

```bash
# RabbitMQ connection URL
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

**Default:** `amqp://guest:guest@localhost:5672/`

**Description:** RabbitMQ connection URL for message queuing (used by gRPC services).

**Used by:** `src.services.order_service.server`

---

### AI/LLM Configuration

At least one AI provider API key is required for AI features:

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# Google Generative AI API Key
GOOGLE_API_KEY=your-google-api-key-here
```

**Description:**
- `OPENAI_API_KEY`: OpenAI API key for GPT models
- `GOOGLE_API_KEY`: Google Generative AI API key for Gemini models

**Used by:** `src.ai.adapters.llm.factory`

**Note:** The system will automatically select an available provider. If both are set, the factory may prefer one over the other based on implementation.

---

## Docker Compose Environment

When using Docker Compose, environment variables can be set in:

1. **`docker-compose.yml`** (for service-specific config)
2. **`.env` file** (loaded automatically by Docker Compose)

### Example docker-compose.yml

```yaml
services:
  app:
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/cryptoflow
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

### Example .env for Docker

```bash
# Database (connect to docker service)
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/cryptoflow

# Redis (connect to docker service)
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/

# AI Keys (from host environment)
OPENAI_API_KEY=${OPENAI_API_KEY}
GOOGLE_API_KEY=${GOOGLE_API_KEY}
```

**Note:** In Docker, use service names (e.g., `db`, `redis`, `rabbitmq`) instead of `localhost`.

---

## Environment-Specific Configurations

### Development

```bash
# .env.development
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/cryptoflow_dev
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
OPENAI_API_KEY=sk-dev-key-here
```

### Production

```bash
# .env.production
DATABASE_URL=postgresql+asyncpg://prod_user:secure_password@prod-db:5432/cryptoflow
REDIS_URL=redis://prod-redis:6379/0
CELERY_BROKER_URL=amqp://prod_user:secure_password@prod-rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://prod-redis:6379/0
OPENAI_API_KEY=sk-prod-key-here
```

**Security Note:** Never commit `.env` files with production credentials to version control!

---

## Loading Environment Variables

### Python (python-dotenv)

The project uses `python-dotenv` to load `.env` files:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file

database_url = os.getenv("DATABASE_URL")
```

### Manual Loading

If not using `python-dotenv`, you can load manually:

```bash
# Linux/Mac
export DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/cryptoflow

# Windows (PowerShell)
$env:DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/cryptoflow"
```

---

## Validation

### Checking Configuration

You can verify your configuration by:

1. **Checking environment variables:**
   ```python
   import os
   print(os.getenv("DATABASE_URL"))
   ```

2. **Running health checks:**
   ```bash
   # Check database connection
   python -c "from src.config import DATABASE_URL; print(DATABASE_URL)"
   ```

3. **Testing services:**
   ```bash
   # Test database connection
   python test_db_connection.py
   ```

---

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify `DATABASE_URL` format
   - Check PostgreSQL is running
   - Verify credentials

2. **Redis Connection Failed**
   - Verify `REDIS_URL` format
   - Check Redis is running
   - Test connection: `redis-cli ping`

3. **AI Features Not Working**
   - Verify at least one API key is set
   - Check API key is valid
   - Verify network connectivity

4. **Celery Tasks Not Running**
   - Verify `CELERY_BROKER_URL` is correct
   - Check RabbitMQ/Redis is running
   - Verify worker is started: `celery -A src.infrastructure.celery_app worker`

---

## Security Best Practices

1. **Never commit `.env` files** - Add to `.gitignore`
2. **Use strong passwords** for production databases
3. **Rotate API keys** regularly
4. **Use secrets management** in production (e.g., AWS Secrets Manager, HashiCorp Vault)
5. **Limit access** to environment variables
6. **Use different keys** for development and production

---

## Example .env File

Complete example `.env` file:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/cryptoflow

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# AI/LLM (choose at least one)
OPENAI_API_KEY=sk-your-openai-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
```

---

## Additional Resources

- [FastAPI Configuration](https://fastapi.tiangolo.com/advanced/settings/)
- [python-dotenv Documentation](https://pypi.org/project/python-dotenv/)
- [Docker Compose Environment Variables](https://docs.docker.com/compose/environment-variables/)

