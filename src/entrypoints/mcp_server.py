#!/usr/bin/env python3
"""
CryptoFlow MCP Server

This module implements a Model Context Protocol (MCP) server using FastMCP.
It demonstrates the four core MCP primitives integrated with hexagonal architecture:
1. Resources - Passive data from domain entities
2. Tools - Active actions via application use cases
3. Prompts - AI-powered templates using RAG
4. Sampling - Inversion of control for sentiment analysis

Architecture Integration:
- Follows hexagonal architecture (Ports & Adapters)
- Uses dependency injection for all services
- Delegates to application layer use cases
- Returns domain entities via DTOs
"""

import json
import asyncio
import logging
import sys
from typing import Optional
from dotenv import load_dotenv

# Configure logging to stderr to avoid interfering with MCP protocol (stdio)
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
try:
    import structlog
    structlog.configure(
        processors=[
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
    )
except ImportError:
    pass

from fastmcp import FastMCP, Context
from mcp.types import TextContent, PromptMessage

# Domain & Application Layer
from src.domain.exceptions import InvalidSymbolError
from src.application.use_cases.get_portfolio import GetPortfolioUseCase
from src.application.use_cases.place_order import PlaceOrderUseCase
from src.application.dtos import OrderCreate

# AI Services
from src.ai.application.rag_service import RAGService
from src.ai.application.agent_service import TraderAgent

# Infrastructure (for bootstrap only)
from src.infrastructure.uow_postgres import SqlAlchemyUnitOfWork
from src.infrastructure.adapters.mock_exchange import MockExchangeAdapter
from src.ai.adapters.vector_store_factory import VectorStoreFactory
from src.ai.adapters.llm.factory import LLMFactory
from src.ai.adapters.trading_tools_adapter import TradingToolAdapter


# ============================================================================
# DEPENDENCY INJECTION - COMPOSITION ROOT
# ============================================================================

class MCPServices:
    """
    Container for all injected services.
    Follows the Composition Root pattern from hexagonal architecture.
    """
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


def bootstrap_mcp() -> MCPServices:
    """
    Bootstrap function - wires all dependencies together.
    
    This is the "Composition Root" where we:
    1. Create infrastructure adapters (outer hexagon)
    2. Inject them into application services (inner hexagon)
    3. Return configured services
    
    Similar to src/ai/main.py:bootstrap_ai()
    """
    load_dotenv()
    
    # Infrastructure Layer (Adapters)
    uow = SqlAlchemyUnitOfWork()
    exchange = MockExchangeAdapter()
    
    # Application Layer (Use Cases)
    portfolio_use_case = GetPortfolioUseCase(uow=uow)
    place_order_use_case = PlaceOrderUseCase(uow=uow, exchange=exchange)
    
    # AI Services (Optional - graceful degradation if not configured)
    rag_service = None
    trader_agent = None
    
    try:
        vector_store = VectorStoreFactory.create_store()
        llm = LLMFactory.create_provider()
        
        if vector_store and llm:
            rag_service = RAGService(vector_store=vector_store, llm_provider=llm)
            trading_tool = TradingToolAdapter()
            trader_agent = TraderAgent(llm_provider=llm, trading_tool=trading_tool)
    except Exception as e:
        print(f"WARNING: AI services not available: {e}")
        print("MCP server will run with limited functionality (no RAG/Agent features)")
    
    return MCPServices(
        portfolio_use_case=portfolio_use_case,
        place_order_use_case=place_order_use_case,
        rag_service=rag_service,
        trader_agent=trader_agent
    )


# Initialize services
services = bootstrap_mcp()

# Initialize FastMCP server
mcp = FastMCP("CryptoFlow MCP")


# ============================================================================
# RESOURCE: Passive Data (Read-Only State)
# ============================================================================
# Resources allow the AI to "read" data without executing actions.
# Integrated with GetPortfolioUseCase for real data.

async def _get_portfolio_data() -> str:
    """Helper to fetch portfolio data (shared by resource and prompt)."""
    try:
        # Delegate to use case (hexagonal architecture pattern)
        portfolio = await services.portfolio_use_case.execute()
        
        # Convert DTO to JSON for MCP protocol
        return json.dumps({
            "holdings": portfolio.holdings,
            "total_assets": portfolio.total_assets,
            "last_updated": portfolio.last_updated
        }, indent=2)
    
    except Exception as e:
        # Graceful error handling
        return json.dumps({
            "error": f"Failed to retrieve portfolio: {str(e)}",
            "holdings": {},
            "total_assets": 0
        }, indent=2)

@mcp.resource("portfolio://current")
async def get_current_portfolio() -> str:
    """
    Returns the current portfolio state from the database.
    
    Architecture:
    - Delegates to GetPortfolioUseCase (application layer)
    - Returns domain data via DTOs
    - Read-only, no side effects
    
    Returns:
        JSON string representing current holdings from database
    """
    return await _get_portfolio_data()


# ============================================================================
# TOOL: Active Action (State-Changing Operation)
# ============================================================================
# Tools execute actions via application use cases.
# Integrated with PlaceOrderUseCase for real order execution.

@mcp.tool()
async def place_order(symbol: str, side: str, amount: float, price: float = 0.0) -> str:
    """
    Execute a trade order via PlaceOrderUseCase.
    
    Architecture:
    - Delegates to PlaceOrderUseCase (application layer)
    - Uses domain entities (Order)
    - Handles domain exceptions
    - Has side effects (modifies database)
    
    Args:
        symbol: Trading pair symbol (e.g., "BTC", "ETH")
        side: Order side - "BUY" or "SELL"
        amount: Amount to trade (quantity)
        price: Limit price (defaults to market price if 0.0)
    
    Returns:
        Confirmation message with order details
    """
    try:
        # Create DTO for use case
        order_data = OrderCreate(
            symbol=symbol.upper(),
            side=side.upper(),
            quantity=amount,
            price=price if price > 0 else 50000.0,  # Default price if not provided
            metadata={"source": "mcp_server"}
        )
        
        # Delegate to use case (hexagonal architecture)
        result = await services.place_order_use_case.execute(order_data)
        
        return f"✓ Order placed successfully!\n" \
               f"Order ID: {result.order_id}\n" \
               f"Action: {result.side} {result.quantity} {result.symbol}\n" \
               f"Price: ${result.price:,.2f}\n" \
               f"Status: {result.status}"
    
    except InvalidSymbolError as e:
        return f"❌ Invalid symbol: {str(e)}"
    
    except ValueError as e:
        return f"❌ Validation error: {str(e)}"
    
    except Exception as e:
        return f"❌ Failed to place order: {str(e)}"


# ============================================================================
# PROMPT: AI-Powered Template
# ============================================================================
# Prompts use RAGService for intelligent, context-aware templates.

@mcp.prompt()
async def daily_briefing() -> list:
    """
    Generate an AI-powered daily portfolio briefing.
    
    Architecture:
    - Fetches real portfolio data via resource
    - Uses RAGService for enhanced context (if available)
    - Returns structured prompt for AI analysis
    
    Returns:
        List containing UserMessage with intelligent briefing
    """
    # Fetch real portfolio data
    portfolio_json = await _get_portfolio_data() # Use helper instead of resource call
    portfolio_data = json.loads(portfolio_json)
    
    # Base briefing text
    briefing_text = f"""Here is the current portfolio:

{json.dumps(portfolio_data, indent=2)}

Please analyze the risk profile of this portfolio and provide:
1. Overall risk assessment (Low/Medium/High)
2. Diversification analysis
3. Recommended actions (if any)
4. Key metrics to monitor

Focus on actionable insights for a crypto trading context."""
    
    # Enhance with RAG if available
    if services.rag_service:
        try:
            # Use RAG to add relevant documentation context
            rag_context = services.rag_service.answer_question(
                "What are the risk management best practices for crypto portfolios?"
            )
            briefing_text += f"\n\n--- Risk Management Context ---\n{rag_context}"
        except Exception as e:
            # Graceful degradation if RAG fails
            print(f"RAG enhancement failed: {e}")
    
    return [
        PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=briefing_text
            )
        )
    ]


# ============================================================================
# SAMPLING: Inversion of Control (Server Asks Client for Intelligence)
# ============================================================================
# Sampling demonstrates the server asking the client's LLM for analysis.

@mcp.tool()
async def analyze_sentiment(text: str, ctx: Context) -> float:
    """
    Analyze sentiment using the client's LLM (sampling/inversion of control).
    
    This demonstrates MCP's "sampling" capability:
    - Server asks CLIENT to use its LLM
    - Client does the AI reasoning
    - Server gets back structured intelligence
    
    Args:
        text: News article or text to analyze
        ctx: MCP Context (provides access to session)
    
    Returns:
        Sentiment score between 0.0 (negative) and 1.0 (positive)
    """
    system_prompt = """You are a financial sentiment analyst specializing in cryptocurrency markets.

Analyze the sentiment of the provided text and return a float score between 0.0 and 1.0:
- 0.0 = Extremely negative (market crash, hacks, regulatory bans)
- 0.5 = Neutral (factual reporting, mixed signals)
- 1.0 = Extremely positive (adoption, price rallies, positive regulation)

Return ONLY the numeric score, nothing else. No explanation, no text, just the number."""
    
    try:
        # Use sampling - ask the CLIENT's LLM for intelligence
        response = await ctx.session.create_message(
            messages=[
                {
                    "role": "system",
                    "content": {
                        "type": "text",
                        "text": system_prompt
                    }
                },
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": text
                    }
                }
            ],
            max_tokens=10
        )
        
        # Extract and validate score
        score_text = response.content.text.strip()
        score = float(score_text)
        
        # Clamp to valid range
        return max(0.0, min(1.0, score))
    
    except (ValueError, AttributeError) as e:
        print(f"Sentiment analysis failed: {e}")
        return 0.5  # Neutral fallback


# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CryptoFlow MCP Server")
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"], help="Transport protocol")
    parser.add_argument("--host", default="0.0.0.0", help="Host for SSE server")
    parser.add_argument("--port", type=int, default=8000, help="Port for SSE server")
    
    args = parser.parse_args()
    
    print("=== CryptoFlow MCP Server ===", file=sys.stderr)
    print("Architecture: Hexagonal (Ports & Adapters)", file=sys.stderr)
    print("Services initialized:", file=sys.stderr)
    print(f"  ✓ Portfolio Use Case", file=sys.stderr)
    print(f"  ✓ Place Order Use Case", file=sys.stderr)
    print(f"  {'✓' if services.rag_service else '✗'} RAG Service", file=sys.stderr)
    print(f"  {'✓' if services.trader_agent else '✗'} Trader Agent", file=sys.stderr)
    
    if args.transport == "sse":
        print(f"\nStarting SSE server on {args.host}:{args.port}...", file=sys.stderr)
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        print("\nListening for MCP protocol messages (STDIO)...", file=sys.stderr)
        mcp.run(transport="stdio")
