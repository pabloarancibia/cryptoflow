# Model Context Protocol (MCP) Implementation

**Module:** `src/entrypoints/mcp_server.py`  
**Status:** Production Ready  
**Protocol Version:** MCP 1.0  
**Framework:** FastMCP

---

## 1. Overview

The CryptoFlow MCP Server exposes the trading platform's capabilities through the **Model Context Protocol (MCP)**, enabling AI assistants like Claude to interact with the system using natural language while maintaining strict adherence to hexagonal architecture principles.

### What is MCP?

Model Context Protocol is an open standard that allows AI applications to securely access external data and tools. It defines four core primitives:

1. **Resources** - Read-only data sources (like API endpoints)
2. **Tools** - Actions that modify state (like function calls)
3. **Prompts** - Reusable templates for AI interactions
4. **Sampling** - Inversion of control where servers request AI assistance

---

## 2. Architecture Integration

The MCP server follows CryptoFlow's hexagonal architecture, acting as an **entrypoint** (delivery mechanism) that delegates to application layer use cases.

### System Architecture

```mermaid
--8<-- "docs/documentation/diagrams/ai/mcp_architecture.mmd"
```

### Key Architectural Principles

- **Dependency Injection**: All services injected via `bootstrap_mcp()` composition root
- **Use Case Delegation**: MCP handlers delegate to application layer use cases
- **Domain Entities**: Returns data using domain DTOs, not raw database models
- **Graceful Degradation**: AI services (RAG, Agent) are optional

---

## 3. MCP Primitives Implementation

### Primitives Mapping

```mermaid
--8<-- "docs/documentation/diagrams/ai/mcp_primitives.mmd"
```

### 3.1 Resources (Read-Only Data)

#### `portfolio://current`

Returns current portfolio holdings from the database.

**Implementation:**
```python
@mcp.resource("portfolio://current")
async def get_current_portfolio() -> str:
    portfolio = await services.portfolio_use_case.execute()
    return json.dumps({
        "holdings": portfolio.holdings,
        "total_assets": portfolio.total_assets,
        "last_updated": portfolio.last_updated
    }, indent=2)
```

**Response Example:**
```json
{
  "holdings": {
    "BTC": 1.5,
    "ETH": 10.0,
    "USD": 50000.0
  },
  "total_assets": 3,
  "last_updated": "2025-12-29T17:31:23+01:00"
}
```

**Architecture:**
- Delegates to `GetPortfolioUseCase`
- Uses `PostgresUnitOfWork` for database access
- Returns `PortfolioResponse` DTO

---

### 3.2 Tools (State-Changing Actions)

#### `place_order`

Executes a trading order through the application layer.

**Signature:**
```python
async def place_order(
    symbol: str,      # Trading pair (e.g., "BTC", "ETH")
    side: str,        # "BUY" or "SELL"
    amount: float,    # Quantity to trade
    price: float = 0.0  # Limit price (optional)
) -> str
```

**Implementation:**
```python
@mcp.tool()
async def place_order(symbol: str, side: str, amount: float, price: float = 0.0) -> str:
    order_data = OrderCreate(
        symbol=symbol.upper(),
        side=side.upper(),
        quantity=amount,
        price=price if price > 0 else 50000.0,
        metadata={"source": "mcp_server"}
    )
    result = await services.place_order_use_case.execute(order_data)
    return f"✓ Order placed successfully!\nOrder ID: {result.order_id}..."
```

**Example Usage:**
```
Client: "Buy 1.5 BTC at $50,000"
Tool Call: place_order("BTC", "BUY", 1.5, 50000.0)
Response: ✓ Order placed successfully!
          Order ID: 3fa85f64-5717-4562-b3fc-2c963f66afa6
          Action: BUY 1.5 BTC
          Price: $50,000.00
          Status: PENDING
```

**Architecture:**
- Delegates to `PlaceOrderUseCase`
- Creates `Order` domain entity
- Persists via `PostgresUnitOfWork`
- Publishes domain event via Celery
- Handles `InvalidSymbolError` and validation errors

---

### 3.3 Prompts (AI Templates)

#### `daily_briefing`

Generates an AI-powered portfolio analysis prompt enhanced with RAG context.

**Implementation:**
```python
@mcp.prompt()
async def daily_briefing() -> list:
    # Fetch real portfolio data
    portfolio_json = await get_current_portfolio()
    portfolio_data = json.loads(portfolio_json)
    
    # Enhance with RAG if available
    if services.rag_service:
        rag_context = services.rag_service.answer_question(
            "What are the risk management best practices for crypto portfolios?"
        )
        briefing_text += f"\n\n--- Risk Management Context ---\n{rag_context}"
    
    return [UserMessage(role="user", content=TextContent(text=briefing_text))]
```

**Features:**
- Combines real portfolio data with AI analysis instructions
- Optionally enhances with RAG-retrieved documentation context
- Provides structured guidance for risk assessment

---

### 3.4 Sampling (Inversion of Control)

#### `analyze_sentiment`

Demonstrates sampling by asking the **client's LLM** to analyze sentiment.

**Signature:**
```python
async def analyze_sentiment(text: str, ctx: Context) -> float
```

**Implementation:**
```python
@mcp.tool()
async def analyze_sentiment(text: str, ctx: Context) -> float:
    response = await ctx.session.create_message(
        messages=[
            {"role": "system", "content": {"type": "text", "text": system_prompt}},
            {"role": "user", "content": {"type": "text", "text": text}}
        ],
        max_tokens=10
    )
    score = float(response.content.text.strip())
    return max(0.0, min(1.0, score))  # Clamp to [0.0, 1.0]
```

**Example:**
```python
# Server asks CLIENT's LLM for intelligence
score = await analyze_sentiment("Bitcoin hits new all-time high!", ctx)
# Returns: 0.95 (very positive)
```

**Key Concept:**
This is **inversion of control** - the server doesn't need its own LLM. It leverages the client's AI capabilities for analysis.

---

## 4. Interaction Flow

### Sequence Diagram

```mermaid
--8<-- "docs/documentation/diagrams/ai/mcp_interaction_flow.mmd"
```

### Flow Explanation

1. **Client Request**: MCP client sends resource/tool request
2. **MCP Server**: Routes to appropriate handler
3. **Use Case**: Handler delegates to application layer use case
4. **Unit of Work**: Use case opens transaction
5. **Database**: Data persisted/retrieved
6. **Response**: DTO returned to client as JSON

---

## 5. Dependency Injection

### Bootstrap Function

The `bootstrap_mcp()` function implements the **Composition Root** pattern:

```python
def bootstrap_mcp() -> MCPServices:
    load_dotenv()
    
    # Infrastructure Layer (Adapters)
    uow = PostgresUnitOfWork()
    exchange = MockExchangeAdapter()
    
    # Application Layer (Use Cases)
    portfolio_use_case = GetPortfolioUseCase(uow=uow)
    place_order_use_case = PlaceOrderUseCase(uow=uow, exchange=exchange)
    
    # AI Services (Optional)
    rag_service = RAGService(vector_store=vector_store, llm_provider=llm)
    trader_agent = TraderAgent(llm_provider=llm, trading_tool=trading_tool)
    
    return MCPServices(
        portfolio_use_case=portfolio_use_case,
        place_order_use_case=place_order_use_case,
        rag_service=rag_service,
        trader_agent=trader_agent
    )
```

### Service Container

```python
class MCPServices:
    """Container for all injected services."""
    def __init__(
        self,
        portfolio_use_case: GetPortfolioUseCase,
        place_order_use_case: PlaceOrderUseCase,
        rag_service: Optional[RAGService] = None,
        trader_agent: Optional[TraderAgent] = None
    ):
        self.portfolio_use_case = portfolio_use_case
        self.place_order_use_case = place_order_use_case
        self.rag_service = rag_service
        self.trader_agent = trader_agent
```

---

## 6. Running the MCP Server

### Prerequisites

- Python 3.11+
- PostgreSQL running
- Environment variables configured (`.env`)
- Optional: ChromaDB for RAG features

### Start Server

```bash
# Activate virtual environment
source venv/bin/activate

# Run MCP server
python src/entrypoints/mcp_server.py
```

### Expected Output

```
=== CryptoFlow MCP Server ===
Architecture: Hexagonal (Ports & Adapters)
Services initialized:
  ✓ Portfolio Use Case
  ✓ Place Order Use Case
  ✓ RAG Service
  ✓ Trader Agent

Listening for MCP protocol messages...
```

---

## 7. Testing

### Unit Tests

```bash
# Test portfolio use case
pytest tests/unit_tests/test_get_portfolio.py -v

# Test all unit tests
pytest tests/unit_tests/ -v
```

### Manual Testing

See [MCP Client Setup Guide](mcp_client_setup.md) for instructions on connecting an MCP client.

---

## 8. Security Considerations

### Authentication

> [!WARNING]
> **Production Deployment**
> 
> The current implementation does not include authentication. For production use, implement:
> - API key authentication
> - Rate limiting
> - Request validation
> - Audit logging

### Input Validation

All tools validate inputs:
- Symbol format validation via `SymbolRegistry`
- Quantity/price positivity checks
- Side validation (BUY/SELL only)

### Error Handling

```python
try:
    result = await services.place_order_use_case.execute(order_data)
except InvalidSymbolError as e:
    return f"❌ Invalid symbol: {str(e)}"
except ValueError as e:
    return f"❌ Validation error: {str(e)}"
except Exception as e:
    return f"❌ Failed to place order: {str(e)}"
```

---

## 9. Future Enhancements

### Planned Features

1. **Additional Resources**
   - `market_data://prices` - Real-time price feeds
   - `orders://history` - Order history
   - `analytics://performance` - Portfolio performance metrics

2. **Additional Tools**
   - `cancel_order(order_id)` - Cancel pending orders
   - `get_market_data(symbol)` - Fetch market data
   - `analyze_portfolio_risk()` - AI-powered risk analysis

3. **Enhanced Prompts**
   - `trading_strategy` - Generate trading strategies
   - `market_analysis` - Comprehensive market analysis
   - `risk_report` - Detailed risk assessment

4. **Authentication & Authorization**
   - JWT-based authentication
   - Role-based access control
   - API key management

---

## 10. References

- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Hexagonal Architecture Guide](hexagonal_architecture.md)
- [AI Module Documentation](ai_module.md)
