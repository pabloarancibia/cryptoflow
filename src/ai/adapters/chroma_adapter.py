__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List
from src.ai.domain.ports import IVectorStore
from src.ai.domain.models import DocumentChunk

class ChromaKBAdapter(IVectorStore):
    def __init__(self, collection_name: str = "project_docs"):
        # Connect to ChromaDB
        # Running locally (or Docker fallback logic)
        try:
            print("Connecting to ChromaDB at localhost:8001...")
            self.client = chromadb.HttpClient(host="localhost", port=8001)
            self.client.heartbeat()
        except Exception:
            print("Fallback to chroma:8000 (Docker network)...")
            self.client = chromadb.HttpClient(host="chroma", port=8000)
            
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def ingest(self, docs: List[DocumentChunk]) -> None:
        if not docs:
            return
            
        documents = [d.content for d in docs]
        metadatas = [d.metadata for d in docs]
        ids = [d.id for d in docs]
        embeddings = self.model.encode(documents).tolist()

        self.collection.upsert(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Ingested {len(docs)} chunks to ChromaDB.")

    def query(self, text: str, n_results: int = 5) -> List[DocumentChunk]:
        query_embeddings = self.model.encode([text]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results
        )
        
        chunks = []
        if results and results['documents']:
            for i, doc_content in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i] if results['metadatas'] else {}
                doc_id = results['ids'][0][i] if results['ids'] else f"id_{i}"
                chunks.append(DocumentChunk(content=doc_content, metadata=meta, id=doc_id))
        
        return chunks
