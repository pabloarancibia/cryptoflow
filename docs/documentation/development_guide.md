# Development Guide

Complete guide for developing and contributing to CryptoFlow.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Database Migrations](#database-migrations)
- [Debugging](#debugging)
- [Code Review Guidelines](#code-review-guidelines)

---

## Development Setup

### Prerequisites

- Python 3.11+ (3.12+ recommended)
- PostgreSQL 15+
- Redis 7+
- RabbitMQ 3+
- Docker & Docker Compose (optional)

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/cryptoflow.git
   cd cryptoflow
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env  # If available
   # Edit .env with your configuration
   ```

5. **Start infrastructure services:**
   ```bash
   docker-compose up -d
   ```

6. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

7. **Verify setup:**
   ```bash
   pytest tests/unit_tests/ -v
   ```

---

## Project Structure

CryptoFlow follows Clean Architecture principles:

```
src/
├── domain/              # Core business logic (Entities, Value Objects, Domain Services)
│   ├── entities.py      # Domain entities (Order, FinancialInstrument)
│   ├── strategies.py    # Trading strategies (Strategy Pattern)
│   ├── services.py       # Domain services
│   └── exceptions.py     # Domain exceptions
│
├── application/         # Application layer (Use Cases, DTOs)
│   ├── use_cases/       # Business use cases
│   ├── dtos.py          # Data Transfer Objects
│   ├── ports/           # Ports (interfaces)
│   └── factories.py     # Factory patterns
│
├── infrastructure/      # Infrastructure layer (Adapters)
│   ├── database.py      # Database connection
│   ├── repositories/    # Repository implementations
│   ├── adapters/        # External service adapters
│   ├── cache.py         # Redis caching
│   └── grpc_client.py   # gRPC client
│
├── entrypoints/         # Entry points (API, CLI)
│   └── api/             # FastAPI routes
│
└── ai/                  # AI module (RAG, Agents)
    ├── domain/          # AI domain models
    ├── application/     # AI use cases
    └── adapters/        # LLM adapters
```

### Key Principles

1. **Dependency Rule**: Dependencies point inward (Domain has no dependencies)
2. **Interface Segregation**: Use ports/interfaces for external dependencies
3. **Single Responsibility**: Each module has one clear purpose
4. **Open/Closed**: Open for extension, closed for modification

---

## Coding Standards

### Python Style

- Follow **PEP 8** style guidelines
- Use **type hints** for all function signatures
- Maximum line length: **100 characters** (configurable)
- Use **black** for code formatting (recommended)

### Code Formatting

```bash
# Install formatting tools
pip install black isort flake8 mypy

# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `OrderService`)
- **Functions/Methods**: `snake_case` (e.g., `place_order`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_ORDER_SIZE`)
- **Private**: Prefix with `_` (e.g., `_internal_method`)

### Documentation

- Use **docstrings** for all public functions, classes, and modules
- Follow **Google-style** docstrings:

```python
def place_order(order_data: OrderCreate) -> OrderResponse:
    """
    Place a new trading order.

    Args:
        order_data: Order creation data

    Returns:
        Created order response

    Raises:
        DomainError: If order validation fails
    """
    pass
```

---

## Development Workflow

### Branch Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Feature branches
- `bugfix/*`: Bug fix branches
- `hotfix/*`: Critical production fixes

### Creating a Feature

1. **Create feature branch:**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make changes:**
   - Write code following coding standards
   - Add tests for new functionality
   - Update documentation if needed

3. **Run tests:**
   ```bash
   pytest
   ```

4. **Commit changes:**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and create PR:**
   ```bash
   git push origin feature/my-new-feature
   # Create Pull Request on GitHub
   ```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example:
```
feat: add RSI trading strategy

- Implement RSIStrategy class
- Add RSI calculation logic
- Add unit tests for RSI strategy
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit_tests/test_strategies.py

# Run with verbose output
pytest -v

# Run only unit tests
pytest tests/unit_tests/

# Run only integration tests
pytest tests/integration_tests/
```

### Writing Tests

1. **Unit Tests**: Test individual components in isolation
   ```python
   def test_moving_average_strategy():
       strategy = MovingAverageStrategy(window=5)
       prices = [100, 105, 110, 115, 120]
       signal = strategy.calculate_signal(prices)
       assert signal == "BUY"
   ```

2. **Integration Tests**: Test component interactions
   ```python
   async def test_place_order_integration():
       # Test full order placement flow
       pass
   ```

3. **Test Fixtures**: Use pytest fixtures for common setup
   ```python
   @pytest.fixture
   def mock_exchange():
       return MockExchangeAdapter()
   ```

See [Testing Strategy](testing_strategy.md) for detailed testing guidelines.

---

## Database Migrations

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "add user table"

# Create empty migration
alembic revision -m "add custom index"
```

### Applying Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

### Migration Best Practices

1. **Review auto-generated migrations** before applying
2. **Test migrations** on a copy of production data
3. **Never edit applied migrations** - create new ones
4. **Use transactions** for data migrations
5. **Document breaking changes** in migration messages

---

## Debugging

### FastAPI Debugging

```python
# Add breakpoints
import pdb; pdb.set_trace()

# Or use debugger
from IPython import embed; embed()
```

### Logging

```python
import logging
from src.infrastructure.logging import configure_logging

configure_logging()
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Database Debugging

```python
# Enable SQL query logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### Performance Profiling

```python
# Use snakeviz for profiling
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats()
```

Then visualize:
```bash
snakeviz profile_output.prof
```

---

## Code Review Guidelines

### For Authors

1. **Keep PRs focused** - One feature or fix per PR
2. **Write clear descriptions** - Explain what and why
3. **Add tests** - New code should have tests
4. **Update documentation** - If behavior changes
5. **Respond to feedback** - Address review comments

### For Reviewers

1. **Be constructive** - Provide actionable feedback
2. **Check tests** - Ensure adequate test coverage
3. **Verify architecture** - Follow Clean Architecture principles
4. **Test locally** - Run tests and verify functionality
5. **Approve promptly** - Don't block on minor issues

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes (or documented)
- [ ] Performance considerations addressed
- [ ] Security concerns addressed
- [ ] Error handling is appropriate

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

---

## Getting Help

- **Documentation**: Check [docs/](../index.md) for detailed guides
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Request review from maintainers

