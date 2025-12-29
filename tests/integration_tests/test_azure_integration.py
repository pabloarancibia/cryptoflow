import sys
import os
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.ai.adapters.vector_store_factory import VectorStoreFactory
from src.ai.adapters.llm.factory import LLMFactory
from src.ai.application.tools.definitions import execute_trade_def
from src.ai.domain.models import DocumentChunk, ToolCall


def test_azure_integration():
    """
    Integration test for Azure AI services.
    
    Requirements:
    - AZURE_OPENAI_ENDPOINT
    - AZURE_OPENAI_API_KEY
    - AZURE_OPENAI_DEPLOYMENT_NAME
    - AZURE_SEARCH_ENDPOINT
    - AZURE_SEARCH_API_KEY
    - AZURE_SEARCH_INDEX_NAME
    """
    print("=== Testing Azure AI Integration ===")
    load_dotenv()
    
    # Check for Azure configuration
    azure_llm_configured = bool(
        os.getenv("AZURE_OPENAI_ENDPOINT") and 
        os.getenv("AZURE_OPENAI_API_KEY")
    )
    azure_search_configured = bool(
        os.getenv("AZURE_SEARCH_ENDPOINT") and 
        os.getenv("AZURE_SEARCH_API_KEY")
    )
    
    if not azure_llm_configured:
        print("SKIPPED: Azure OpenAI not configured")
        print("Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY to run this test")
        return
    
    if not azure_search_configured:
        print("WARNING: Azure AI Search not configured, will use ChromaDB fallback")
    
    # Test 1: Vector Store
    print("\n--- Test 1: Vector Store Initialization ---")
    vector_store = VectorStoreFactory.create_store()
    if not vector_store:
        print("ERROR: No Vector Store created")
        return
    
    print(f"Vector Store: {vector_store.__class__.__name__}")
    
    # Test 2: Document Ingestion
    print("\n--- Test 2: Document Ingestion ---")
    test_docs = [
        DocumentChunk(
            id="test-1",
            content="Bitcoin is a decentralized cryptocurrency.",
            metadata={"source": "test", "type": "crypto"}
        ),
        DocumentChunk(
            id="test-2",
            content="Ethereum supports smart contracts and DeFi applications.",
            metadata={"source": "test", "type": "crypto"}
        )
    ]
    
    try:
        vector_store.ingest(test_docs)
        print("SUCCESS: Documents ingested")
    except Exception as e:
        print(f"ERROR: Ingestion failed: {e}")
        return
    
    # Test 3: Vector Search
    print("\n--- Test 3: Vector Search ---")
    query = "What is Bitcoin?"
    try:
        results = vector_store.query(query, n_results=2)
        print(f"Query: {query}")
        print(f"Results: {len(results)} documents")
        for i, doc in enumerate(results):
            print(f"  {i+1}. {doc.content[:50]}...")
        print("SUCCESS: Search completed")
    except Exception as e:
        print(f"ERROR: Search failed: {e}")
    
    # Test 4: LLM Provider
    print("\n--- Test 4: LLM Provider Initialization ---")
    llm = LLMFactory.create_provider()
    if not llm:
        print("ERROR: No LLM Provider created")
        return
    
    print(f"LLM Provider: {llm.__class__.__name__}")
    
    # Test 5: Text Generation
    print("\n--- Test 5: Text Generation ---")
    prompt = "Say 'Hello from Azure' in one sentence."
    try:
        response = llm.generate_text(prompt)
        print(f"Prompt: {prompt}")
        print(f"Response: {response}")
        print("SUCCESS: Text generation completed")
    except Exception as e:
        print(f"ERROR: Text generation failed: {e}")
    
    # Test 6: Tool Calling
    print("\n--- Test 6: Tool Calling ---")
    trade_prompt = "I want to buy 2.5 BTC"
    try:
        response = llm.generate_with_tools(
            prompt=trade_prompt,
            tools=[execute_trade_def],
            system_instruction="You are a trading agent."
        )
        
        print(f"Prompt: {trade_prompt}")
        print(f"Response Type: {type(response).__name__}")
        
        if isinstance(response, ToolCall):
            print("SUCCESS: Tool call detected")
            print(f"  Function: {response.name}")
            print(f"  Arguments: {response.arguments}")
        else:
            print(f"FAILURE: Expected ToolCall, got text: {response}")
    except Exception as e:
        print(f"ERROR: Tool calling failed: {e}")
    
    # Test 7: Chitchat (no tool)
    print("\n--- Test 7: Chitchat (No Tool) ---")
    chat_prompt = "Hello, how are you?"
    try:
        response = llm.generate_with_tools(
            prompt=chat_prompt,
            tools=[execute_trade_def],
            system_instruction="You are a trading agent. If not about trading, just chat."
        )
        
        print(f"Prompt: {chat_prompt}")
        print(f"Response Type: {type(response).__name__}")
        
        if isinstance(response, str):
            print("SUCCESS: Text response")
            print(f"  Response: {response}")
        else:
            print("FAILURE: Expected text, got ToolCall")
    except Exception as e:
        print(f"ERROR: Chitchat failed: {e}")
    
    print("\n=== Azure Integration Test Complete ===")


if __name__ == "__main__":
    test_azure_integration()
