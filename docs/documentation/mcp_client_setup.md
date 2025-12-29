# MCP Client Setup Guide

This guide walks you through setting up an MCP client to connect to the CryptoFlow MCP Server.

---

## Option 1: Claude Desktop (Recommended)

Claude Desktop is the official MCP client from Anthropic with native support for the Model Context Protocol.

### Prerequisites

- macOS 10.15+ or Windows 10+
- Python 3.11+ installed
- CryptoFlow project set up

### Step 1: Install Claude Desktop

Download and install Claude Desktop:
- **macOS**: [Download from Anthropic](https://claude.ai/download)
- **Windows**: [Download from Anthropic](https://claude.ai/download)

### Step 2: Configure MCP Server

Create or edit the Claude Desktop configuration file:

**macOS:**
```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
code %APPDATA%\Claude\claude_desktop_config.json
```

### Step 3: Add CryptoFlow MCP Server

Add the following configuration:

```json
{
  "mcpServers": {
    "cryptoflow": {
      "command": "python",
      "args": [
        "/absolute/path/to/cryptoflow/src/entrypoints/mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/cryptoflow",
        "DATABASE_URL": "postgresql+asyncpg://user:password@localhost:5432/cryptoflow",
        "REDIS_URL": "redis://localhost:6379/0"
      }
    }
  }
}
```

> [!IMPORTANT]
> **Replace Paths**
> 
> - Replace `/absolute/path/to/cryptoflow` with your actual project path
> - Update `DATABASE_URL` with your PostgreSQL credentials
> - Ensure all environment variables from `.env` are included

### Step 4: Restart Claude Desktop

1. Quit Claude Desktop completely
2. Relaunch the application
3. Look for the MCP server indicator in the UI

### Step 5: Verify Connection

In Claude Desktop, try these commands:

```
Can you show me my current portfolio?
```

Claude should use the `portfolio://current` resource to fetch your holdings.

```
Please place an order to buy 0.5 BTC at $50,000
```

Claude should use the `place_order` tool to execute the trade.

---

## Option 2: Custom Python Client

For development and testing, you can create a custom MCP client.

### Installation

```bash
pip install mcp anthropic
```

### Basic Client Example

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Configure server connection
    server_params = StdioServerParameters(
        command="python",
        args=["src/entrypoints/mcp_server.py"],
        env={"PYTHONPATH": "."}
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            
            # List available resources
            resources = await session.list_resources()
            print("Available Resources:", resources)
            
            # Read portfolio resource
            portfolio = await session.read_resource("portfolio://current")
            print("Portfolio:", portfolio.contents[0].text)
            
            # List available tools
            tools = await session.list_tools()
            print("Available Tools:", [t.name for t in tools])
            
            # Call place_order tool
            result = await session.call_tool(
                "place_order",
                arguments={
                    "symbol": "BTC",
                    "side": "BUY",
                    "amount": 0.5,
                    "price": 50000.0
                }
            )
            print("Order Result:", result.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())
```

### Running the Client

```bash
python mcp_client_example.py
```

---

## Option 3: MCP Inspector (Development Tool)

The MCP Inspector is a web-based tool for testing MCP servers.

### Installation

### Helper Script (Recommended)

We provide a helper script that automatically configures the correct Python environment:

```bash
./scripts/inspector.sh
```

### Manual Usage

If you prefer to run it manually:

1. Start the inspector:
   ```bash
   npx @modelcontextprotocol/inspector <path_to_venv_python> <path_to_server_script>
   ```

2. Or via the UI:
   - Start: `npx @modelcontextprotocol/inspector`
   - Command: `/absolute/path/to/venv/bin/python3`
   - Args: `["/absolute/path/to/src/entrypoints/mcp_server.py"]`
   - Env: `PYTHONPATH=/absolute/path/to/project_root`

---

## Available MCP Features

### Resources (Read-Only)

| URI | Description | Returns |
|-----|-------------|---------|
| `portfolio://current` | Current portfolio holdings | JSON with BTC, ETH, USD holdings |

### Tools (Actions)

| Tool | Arguments | Description |
|------|-----------|-------------|
| `place_order` | `symbol`, `side`, `amount`, `price` | Execute a trading order |
| `analyze_sentiment` | `text`, `ctx` | Analyze sentiment using client's LLM |

### Prompts (Templates)

| Prompt | Description |
|--------|-------------|
| `daily_briefing` | AI-powered portfolio risk analysis with RAG context |

---

## Testing Your Setup

### Test 1: Resource Access

**Command in Claude:**
```
Show me my current portfolio
```

**Expected Response:**
```
Your current portfolio contains:
- BTC: 1.5
- ETH: 10.0
- USD: 50,000.00
Total assets: 3
Last updated: 2025-12-29T17:31:23+01:00
```

### Test 2: Tool Execution

**Command in Claude:**
```
Buy 0.5 BTC at market price
```

**Expected Response:**
```
✓ Order placed successfully!
Order ID: 3fa85f64-5717-4562-b3fc-2c963f66afa6
Action: BUY 0.5 BTC
Price: $50,000.00
Status: PENDING
```

### Test 3: Prompt Usage

**Command in Claude:**
```
Use the daily_briefing prompt
```

**Expected Response:**
Claude will analyze your portfolio with risk assessment, diversification analysis, and recommendations.

### Test 4: Sampling

**Command in Claude:**
```
Analyze the sentiment of this text: "Bitcoin reaches new all-time high amid institutional adoption"
```

**Expected Response:**
```
Sentiment score: 0.92 (Very Positive)
```

---

## Troubleshooting

### Server Not Starting

**Issue:** Claude Desktop shows "Server failed to start"

**Solutions:**
1. Check Python path in config is correct
2. Verify all environment variables are set
3. Check server logs: `tail -f /tmp/mcp_server.log`
4. Ensure PostgreSQL is running: `pg_isready`

### Connection Refused

**Issue:** Client cannot connect to server

**Solutions:**
1. Verify server is running: `ps aux | grep mcp_server`
2. Check firewall settings
3. Ensure no port conflicts

### Resource Not Found

**Issue:** `portfolio://current` returns error

**Solutions:**
1. Check database connection
2. Verify `GetPortfolioUseCase` is initialized
3. Check logs for exceptions

### Tool Execution Fails

**Issue:** `place_order` returns error

**Solutions:**
1. Verify symbol is valid (3-5 characters)
2. Check side is "BUY" or "SELL"
3. Ensure amount and price are positive
4. Check database write permissions

---

## Advanced Configuration

### Environment Variables

Add these to the `env` section in Claude Desktop config:

```json
{
  "env": {
    "DATABASE_URL": "postgresql+asyncpg://user:password@localhost:5432/cryptoflow",
    "REDIS_URL": "redis://localhost:6379/0",
    "OPENAI_API_KEY": "your_openai_key",
    "GOOGLE_API_KEY": "your_google_key",
    "LOG_LEVEL": "INFO"
  }
}
```

### Multiple Servers

You can configure multiple MCP servers:

```json
{
  "mcpServers": {
    "cryptoflow": {
      "command": "python",
      "args": ["src/entrypoints/mcp_server.py"]
    },
    "other-service": {
      "command": "node",
      "args": ["other-mcp-server.js"]
    }
  }
}
```

---

## Security Best Practices

### Production Deployment

> [!WARNING]
> **Security Considerations**
> 
> For production use:
> - Use environment-specific configs (dev/staging/prod)
> - Store credentials in secure vaults (not in config files)
> - Implement API key authentication
> - Enable audit logging
> - Use HTTPS for remote connections

### Recommended Setup

1. **Separate Environments**
   ```json
   {
     "mcpServers": {
       "cryptoflow-dev": { "env": { "ENV": "development" } },
       "cryptoflow-prod": { "env": { "ENV": "production" } }
     }
   }
   ```

2. **Credential Management**
   - Use `.env` files (never commit to git)
   - Use secret management tools (AWS Secrets Manager, HashiCorp Vault)
   - Rotate credentials regularly

3. **Monitoring**
   - Enable structured logging
   - Set up alerts for errors
   - Monitor tool execution rates

---

## Next Steps

- [MCP Implementation Documentation](mcp_implementation.md) - Technical details
- [AI Module Guide](ai_module.md) - RAG and Agent features
- [API Reference](api_reference.md) - REST API endpoints

---

## Support

For issues or questions:
- Check [Troubleshooting](#troubleshooting) section
- Review server logs
- Open an issue on GitHub
