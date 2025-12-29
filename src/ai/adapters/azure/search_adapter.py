import os
from typing import List
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
)
from azure.core.credentials import AzureKeyCredential
from sentence_transformers import SentenceTransformer
from src.ai.domain.ports import IVectorStore
from src.ai.domain.models import DocumentChunk


class AzureSearchAdapter(IVectorStore):
    """Azure AI Search adapter implementing IVectorStore interface."""
    
    def __init__(
        self,
        endpoint: str = None,
        api_key: str = None,
        index_name: str = None,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize Azure AI Search adapter.
        
        Args:
            endpoint: Azure Search endpoint (from env if not provided)
            api_key: Azure Search API key (from env if not provided)
            index_name: Index name (from env if not provided)
            embedding_model: Sentence transformer model for embeddings
        """
        self.endpoint = endpoint or os.getenv("AZURE_SEARCH_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_SEARCH_API_KEY")
        self.index_name = index_name or os.getenv("AZURE_SEARCH_INDEX_NAME", "cryptoflow-docs")
        
        if not self.endpoint or not self.api_key:
            raise ValueError("Azure Search endpoint and API key must be provided or set in environment")
        
        self.credential = AzureKeyCredential(self.api_key)
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Initialize clients
        self.index_client = SearchIndexClient(
            endpoint=self.endpoint,
            credential=self.credential
        )
        self.search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=self.credential
        )
        
        # Ensure index exists
        self._ensure_index_exists()
    
    def _ensure_index_exists(self) -> None:
        """Create the search index if it doesn't exist."""
        try:
            self.index_client.get_index(self.index_name)
            print(f"Azure Search: Index '{self.index_name}' already exists.")
        except Exception:
            print(f"Azure Search: Creating index '{self.index_name}'...")
            self._create_index()
    
    def _create_index(self) -> None:
        """Create a new search index with vector search configuration."""
        # Vector dimensions for all-MiniLM-L6-v2
        vector_dimensions = 384
        
        fields = [
            SearchField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True
            ),
            SearchField(
                name="content",
                type=SearchFieldDataType.String,
                searchable=True
            ),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=vector_dimensions,
                vector_search_profile_name="default-profile"
            ),
            SearchField(
                name="source",
                type=SearchFieldDataType.String,
                filterable=True,
                facetable=True
            ),
            SearchField(
                name="metadata",
                type=SearchFieldDataType.String,
                searchable=False
            )
        ]
        
        # Configure vector search
        vector_search = VectorSearch(
            profiles=[
                VectorSearchProfile(
                    name="default-profile",
                    algorithm_configuration_name="hnsw-config"
                )
            ],
            algorithms=[
                HnswAlgorithmConfiguration(name="hnsw-config")
            ]
        )
        
        index = SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=vector_search
        )
        
        self.index_client.create_index(index)
        print(f"Azure Search: Index '{self.index_name}' created successfully.")
    
    def ingest(self, docs: List[DocumentChunk]) -> None:
        """
        Ingest documents into Azure AI Search.
        
        Args:
            docs: List of DocumentChunk objects to ingest
        """
        if not docs:
            return
        
        # Convert to Azure Search documents
        search_docs = []
        for doc in docs:
            # Generate embedding
            embedding = self.embedding_model.encode(doc.content).tolist()
            
            # Convert metadata to JSON string for storage
            import json
            metadata_str = json.dumps(doc.metadata)
            
            search_doc = {
                "id": doc.id,
                "content": doc.content,
                "content_vector": embedding,
                "source": doc.metadata.get("source", "unknown"),
                "metadata": metadata_str
            }
            search_docs.append(search_doc)
        
        # Upload to Azure Search
        try:
            self.search_client.upload_documents(documents=search_docs)
            print(f"Azure Search: Ingested {len(docs)} documents.")
        except Exception as e:
            print(f"Azure Search Error during ingestion: {e}")
            raise
    
    def query(self, text: str, n_results: int = 5) -> List[DocumentChunk]:
        """
        Query Azure AI Search using hybrid search.
        
        Args:
            text: Query text
            n_results: Number of results to return
            
        Returns:
            List of DocumentChunk objects
        """
        import json
        
        # Generate query embedding
        query_vector = self.embedding_model.encode(text).tolist()
        
        try:
            # Perform hybrid search (vector + keyword)
            results = self.search_client.search(
                search_text=text,
                vector_queries=[{
                    "vector": query_vector,
                    "k_nearest_neighbors": n_results,
                    "fields": "content_vector"
                }],
                top=n_results
            )
            
            chunks = []
            for result in results:
                # Parse metadata back from JSON
                metadata = json.loads(result.get("metadata", "{}"))
                
                chunk = DocumentChunk(
                    content=result["content"],
                    metadata=metadata,
                    id=result["id"]
                )
                chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            print(f"Azure Search Error during query: {e}")
            return []
