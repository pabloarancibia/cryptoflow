import asyncio
import os
import sys

# Add project root to python path to run server correctly
sys.path.append(os.getcwd())

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_client():
    print("🚀 Starting MCP Client Test...")
    
    # Define server parameters
    server_params = StdioServerParameters(
        command="venv/bin/python3",
        args=["src/entrypoints/mcp_server.py"],
        env={**os.environ, "PYTHONPATH": "."}
    )
    
    print(f"🔌 Connecting to server: {' '.join(server_params.args)}")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 1. Initialize
            await session.initialize()
            print("✅ Session Initialized")
            
            # 2. List Resources
            resources = await session.list_resources()
            print(f"\n📚 Found {len(resources.resources)} Resources:")
            for res in resources.resources:
                print(f"  - {res.name} ({res.uri})")
            
            # 3. Read specific resource
            print("\n📖 Reading 'portfolio://current'...")
            try:
                content = await session.read_resource("portfolio://current")
                print(f"   Result: {content.contents[0].text[:100]}...")
            except Exception as e:
                print(f"   ❌ Failed: {e}")

            # 4. List Tools
            tools = await session.list_tools()
            print(f"\n🔧 Found {len(tools.tools)} Tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description[:50]}...")
            
            # 5. Execute Tool (Place Order)
            print("\n🔨 Executing 'place_order' (BTC BUY 0.5)...")
            try:
                result = await session.call_tool(
                    "place_order",
                    arguments={"symbol": "BTC", "side": "BUY", "amount": 0.5}
                )
                print("   Result:")
                for content in result.content:
                    if content.type == "text":
                        print(f"   {content.text}")
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                
            # 6. List Prompts
            prompts = await session.list_prompts()
            print(f"\n📝 Found {len(prompts.prompts)} Prompts:")
            for prompt in prompts.prompts:
                print(f"  - {prompt.name}")
                
            # 7. Get Prompt
            print("\n🗣️ Fetching 'daily_briefing' prompt...")
            try:
                prompt_res = await session.get_prompt("daily_briefing")
                print(f"   Message count: {len(prompt_res.messages)}")
                if prompt_res.messages:
                    # In mcp>=1.0.0 messages are structured objects
                    msg = prompt_res.messages[0]
                    # Check msg content type
                    if hasattr(msg, 'content') and hasattr(msg.content, 'text'):
                         print(f"   Preview: {msg.content.text[:100]}...")
                    else:
                         print(f"   Preview: {str(msg)[:100]}...")

            except Exception as e:
                print(f"   ❌ Failed: {e}")

            print("\n✅ Test Complete!")

if __name__ == "__main__":
    asyncio.run(run_client())
