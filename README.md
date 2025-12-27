# CryptoFlow — High-Frequency Trading Engine

CryptoFlow is a modular, high-performance trading simulation system designed to demonstrate advanced Software Engineering principles in Python. The project emphasizes Clean Architecture, Gang of Four (GoF) Design Patterns, and strict Object-Oriented Programming (OOP) to create a scalable, transactional trading engine.

## 🚀 Key Features

- **Polymorphic Asset Modeling**: Abstract handling of Crypto and Fiat currencies using strict OOP with `FinancialInstrument` ABC
- **Memory Optimization**: Utilizes `__slots__` and Generators for processing high-volume market data with low memory footprint
- **Pluggable Strategies**: Strategy Pattern implementation allowing hot-swapping of algorithms (RSI, Moving Average)
- **Resilient Architecture**: Transactional safety via custom Context Managers and transactional rollbacks
- **Event-Driven**: Asynchronous task processing using Celery, RabbitMQ/Redis, and Observer patterns
- **Cloud Native**: Fully containerized with Docker Compose and ready for Kubernetes deployment
- **AI-Powered**: RAG (Retrieval-Augmented Generation) system for documentation search and agentic trading workflows
- **Microservices Ready**: gRPC-based microservices architecture for Market Data and Order services

## 🛠 Tech Stack

- **Language**: Python 3.11+
- **Web Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy 2.0 (Async)
- **Migrations**: Alembic
- **Caching & Locking**: Redis
- **Task Queue**: Celery with RabbitMQ/Redis
- **Vector Database**: ChromaDB (for RAG)
- **AI/ML**: OpenAI API, Google Generative AI, Sentence Transformers
- **RPC**: gRPC with Protocol Buffers
- **Infrastructure**: Docker, Docker Compose
- **Documentation**: MkDocs with Material theme

## 📂 Project Structure (Clean Architecture)

```
cryptoflow/
├── src/
│   ├── domain/              # Enterprise business logic (Entities, Value Objects, Strategies)
│   ├── application/         # Application business logic (Use Cases, DTOs, Ports)
│   ├── infrastructure/      # DB, External APIs, Redis, gRPC clients
│   ├── entrypoints/         # API routes, middleware, error handlers
│   ├── ai/                  # AI Agent & Knowledge Base (RAG)
│   ├── services/            # gRPC microservices (Market Data, Order Service)
│   ├── generated/           # Generated gRPC code from protos
│   ├── scripts/              # Utility scripts (seeding, benchmarking)
│   └── utils/               # Helper utilities
├── tests/                    # Unit and Integration tests
│   ├── unit_tests/          # Fast, isolated unit tests
│   └── integration_tests/    # Full-stack integration tests
├── docs/                     # Documentation (MkDocs)
│   ├── documentation/       # Technical documentation
│   └── wiki/                # Architecture evolution notes
├── protos/                   # Protocol Buffer definitions
├── migrations/               # Alembic database migrations
├── data/                     # Local data storage (ignored by git)
├── docker-compose.yml        # Docker services configuration
├── mkdocs.yml                # MkDocs configuration
├── requirements.txt          # Python dependencies
└── main.py                   # FastAPI application entry point
```


## ⚡ Quick Start

### Prerequisites

- **Python 3.11+** (Python 3.12+ recommended)
- **Docker & Docker Compose** (for running services)
- **PostgreSQL** (or use Docker Compose)
- **Redis** (or use Docker Compose)
- **RabbitMQ** (or use Docker Compose)
- **ChromaDB** (or use Docker Compose)

### Local Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/cryptoflow.git
cd cryptoflow
```

#### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/cryptoflow

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# RabbitMQ (for gRPC services)
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# AI/LLM (choose one or both)
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

> **Note**: See [Environment Variables Guide](docs/documentation/environment_variables.md) for detailed configuration options.

#### 5. Start Infrastructure Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- RabbitMQ (ports 5672, 15672 for management UI)
- ChromaDB (port 8001)

#### 6. Run Database Migrations

```bash
alembic upgrade head
```

#### 7. Run the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

#### 8. (Optional) Start gRPC Services

In separate terminals:

```bash
# Market Data Service
python -m src.services.market_data_service.server

# Order Service
python -m src.services.order_service.server
```

#### 9. (Optional) Start Celery Worker

```bash
celery -A src.infrastructure.celery_app worker --loglevel=info
```

### Docker Setup (Alternative)

For a fully containerized setup:

```bash
docker-compose up --build
```

> **Note**: You may need to configure additional environment variables in `docker-compose.yml` for production use.


## 📚 Documentation

Comprehensive documentation is available via MkDocs. To view it locally:

```bash
mkdocs serve
```

Then open `http://localhost:8000` in your browser.

### Documentation Sections

- **[Architecture Overview](docs/documentation/hexagonal_architecture.md)**: Clean Architecture and Hexagonal Architecture patterns
- **[Microservices Guide](docs/documentation/microservices_theory.md)**: Theory and implementation of microservices with gRPC
- **[AI Module](docs/documentation/ai_module.md)**: RAG system and agentic workflows
- **[API Reference](docs/documentation/api_reference.md)**: Complete API endpoint documentation
- **[Testing Strategy](docs/documentation/testing_strategy.md)**: Testing approach and best practices
- **[Development Guide](docs/documentation/development_guide.md)**: Development workflow and guidelines

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit_tests/

# Run only integration tests
pytest tests/integration_tests/

# Run with coverage
pytest --cov=src --cov-report=html
```

See [Testing Strategy](docs/documentation/testing_strategy.md) for more details.

## 🔌 API Endpoints

### Health Check
```bash
GET /
```

### Trading Endpoints

- **Place Order**: `POST /api/v1/orders`
- **Analyze Market**: `POST /api/v1/analyze`
- **Run Backtest**: `POST /api/v1/backtest`

See [API Reference](docs/documentation/api_reference.md) for detailed endpoint documentation with request/response examples.

## 🗺️ Implementation Status

### ✅ Completed Features

- [x] **Week 1**: FinancialInstrument ABC, Order class with `__slots__`, MarketDataReader with Generators, TransactionSession Context Manager
- [x] **Week 2**: Strategy Pattern (MovingAverageStrategy, RSIStrategy), Factory Pattern, Adapter Pattern, FastAPI Dependency Injection
- [x] **Week 3**: Repository Pattern, Database Session Manager, Redis Caching
- [x] **Week 4**: Observer Pattern, Celery/RabbitMQ integration, Distributed Locking
- [x] **Week 5**: Docker Compose containerization
- [x] **Week 7**: RAG system, Trader Agent with Tool Use Pattern, Async integration

### 🚧 In Progress / Planned

- [ ] **Week 6**: Kubernetes deployment configurations
- [ ] CI/CD pipelines (GitHub Actions)
- [ ] Terraform infrastructure provisioning
- [ ] Blue/Green deployment strategy
- [ ] Additional exchange adapters (Binance, Coinbase)

## 🛠️ Development

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit_tests/test_strategies.py

# Run with coverage
pytest --cov=src --cov-report=term-missing
```

### Code Quality

The project follows PEP 8 style guidelines. Consider using:

- `black` for code formatting
- `flake8` or `pylint` for linting
- `mypy` for type checking

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Building Documentation

```bash
# Serve documentation locally
mkdocs serve

# Build static documentation
mkdocs build
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Project**
2. **Create your Feature Branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your Changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the Branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

Please ensure:
- All tests pass
- Code follows project style guidelines
- Documentation is updated if needed
- New features include appropriate tests

## 📄 License

Distributed under the MIT License. See `LICENSE` file for more information.

## 🔗 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [gRPC Python Guide](https://grpc.io/docs/languages/python/)
- [Celery Documentation](https://docs.celeryq.dev/)

## 📧 Contact & Support

For questions, issues, or contributions, please open an issue on GitHub.