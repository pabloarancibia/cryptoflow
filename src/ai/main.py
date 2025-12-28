from dotenv import load_dotenv
import glob
import os

from src.ai.adapters.vector_store_factory import VectorStoreFactory
from src.ai.adapters.llm.factory import LLMFactory
from src.ai.adapters.trading_tools_adapter import TradingToolAdapter
from src.ai.application.rag_service import RAGService
from src.ai.application.agent_service import TraderAgent
from src.ai.domain.models import DocumentChunk

def bootstrap_ai():
    """Initializes and wires up the AI module components."""
    load_dotenv()
    
    # 1. Initialize Adapters
    vector_store = VectorStoreFactory.create_store()
    if not vector_store:
        print("WARNING: No Vector Store configured. RAG features will not work.")
    
    llm = LLMFactory.create_provider()
    if not llm:
        print("WARNING: No LLM Provider configured. AI features will not work.")
        raise ValueError("Could not create LLM Provider. Check .env for API keys.")

    tools = TradingToolAdapter()
    
    # 2. Inject into Application Services
    rag_service = RAGService(vector_store=vector_store, llm_provider=llm)
    trader_agent = TraderAgent(llm_provider=llm, trading_tool=tools)
    
    return rag_service, trader_agent, vector_store

def ingest_existing_docs(vector_store, docs_path="docs"):
    """Helper to ingest docs if needed."""
    print(f"Checking for docs in {docs_path}...")
    md_files = glob.glob(os.path.join(docs_path, "**/*.md"), recursive=True)
    chunks = []
    
    for file_path in md_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Simple chunking
            file_chunks = content.split("\n\n")
            for i, chunk in enumerate(file_chunks):
                if len(chunk.strip()) > 50:
                    chunks.append(DocumentChunk(
                        content=chunk.strip(),
                        metadata={"source": file_path, "index": i},
                        id=f"{os.path.basename(file_path)}_{i}"
                    ))
    
    if chunks:
        vector_store.ingest(chunks)

def run_demo():
    """Main entry point for the AI Demo."""
    print("=== Cryptoflow AI Demo (Hexagonal Architecture) ===")
    
    rag, agent, vector_store = bootstrap_ai()
    
    # Optional: Ingest docs just to be sure there's data
    # ingest_existing_docs(vector_store)

    print("\n--- Test 1: RAG Question ---")
    question = "How does the matching engine work?"
    print(f"User: {question}")
    answer = rag.answer_question(question)
    print(f"AI: {answer}")
    
    print("\n--- Test 2: Trader Agent ---")
    command = "Buy 1.5 BTC"
    print(f"User: {command}")
    response = agent.run(command)
    print(f"AI: {response.response_text}")

if __name__ == "__main__":
    run_demo()
