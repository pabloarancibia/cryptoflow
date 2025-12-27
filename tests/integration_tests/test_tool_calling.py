import sys
import os
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.ai.adapters.llm.factory import LLMFactory
from src.ai.application.tools.definitions import execute_trade_def
from src.ai.domain.models import ToolCall

def test_tool_calling():
    print("=== Testing Native Function Calling ===")
    load_dotenv()
    
    llm = LLMFactory.create_provider()
    if not llm:
        print("ERROR: No LLM Provider found.")
        return

    print(f"Provider: {llm.__class__.__name__}")
    
    # Test 1: Trading Request
    print("\n--- Test 1: Trading Request ---")
    prompt = "I want to buy 1.5 BTC."
    print(f"Prompt: {prompt}")
    
    response = llm.generate_with_tools(
        prompt=prompt,
        tools=[execute_trade_def],
        system_instruction="You are a trading agent."
    )
    
    print(f"Response Type: {type(response)}")
    print(f"Response: {response}")
    
    if isinstance(response, ToolCall):
        print("SUCCESS: Received ToolCall")
        if response.name == "execute_trade":
            print("SUCCESS: Correct tool name")
        else:
            print("FAILURE: Incorrect tool name")
    else:
        print("FAILURE: Expected ToolCall, got text")

    # Test 2: Chitchat
    print("\n--- Test 2: Chitchat ---")
    prompt = "Hello, how are you?"
    print(f"Prompt: {prompt}")
    
    response = llm.generate_with_tools(
        prompt=prompt,
        tools=[execute_trade_def],
        system_instruction="You are a trading agent. If not about trading, just chat."
    )
    
    print(f"Response Type: {type(response)}")
    print(f"Response: {response}")
    
    if isinstance(response, str):
        print("SUCCESS: Received text response")
    else:
        print("FAILURE: Expected text, got ToolCall")

if __name__ == "__main__":
    test_tool_calling()
