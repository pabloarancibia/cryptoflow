import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ai.knowledge_base import ProjectDocumentationDB
from src.ai.trader_agent import SimulatedAgent

def main():
    print("=== 1. Vector Database / RAG Demo ===")
    kb = ProjectDocumentationDB(docs_path="docs/")
    kb.ingest_docs()
    
    # Query about architecture
    kb.query("How does the gRPC work?")

    print("\n\n=== 2. Intelligent Agent Demo ===")
    agent = SimulatedAgent()
    
    prompt = "Please place a SELL order for 1 BTC"
    response = agent.run(prompt)
    
    print("\n[Final Agent Response]:", response)

if __name__ == "__main__":
    main()
