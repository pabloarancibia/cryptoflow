import os
from typing import Optional
from src.ai.domain.ports import IVectorStore
from src.ai.adapters.chroma_adapter import ChromaKBAdapter


class VectorStoreFactory:
    """Factory for creating vector store instances based on configuration."""
    
    @staticmethod
    def create_store() -> Optional[IVectorStore]:
        """
        Create a vector store instance based on available configuration.
        
        Priority:
        1. Azure AI Search (if AZURE_SEARCH_ENDPOINT is set)
        2. ChromaDB (fallback)
        
        Returns:
            IVectorStore instance or None if no configuration found
        """
        # Check for Azure AI Search
        azure_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        azure_key = os.getenv("AZURE_SEARCH_API_KEY")
        
        if azure_endpoint and azure_key:
            try:
                from src.ai.adapters.azure.search_adapter import AzureSearchAdapter
                print("VectorStoreFactory: Using Azure AI Search")
                return AzureSearchAdapter(
                    endpoint=azure_endpoint,
                    api_key=azure_key
                )
            except ImportError as e:
                print(f"VectorStoreFactory: Azure Search adapter not available: {e}")
                print("VectorStoreFactory: Falling back to ChromaDB")
        
        # Fallback to ChromaDB
        try:
            print("VectorStoreFactory: Using ChromaDB")
            return ChromaKBAdapter()
        except Exception as e:
            print(f"VectorStoreFactory: Error creating ChromaDB adapter: {e}")
            return None
