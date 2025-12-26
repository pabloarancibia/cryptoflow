import os
import glob
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

class ProjectDocumentationDB:
    def __init__(self, docs_path="docs/"):
        self.docs_path = docs_path
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Connect to ChromaDB
        # Try connecting to 'chroma' host (Docker service name) first
        try:
            print("Attempting to connect to ChromaDB at chroma:8000...")
            self.chroma_client = chromadb.HttpClient(host="chroma", port=8000)
            self.chroma_client.heartbeat()
            print("Connected to ChromaDB at chroma:8000")
        except Exception:
            print("Could not connect to chroma:8000, falling back to localhost:8000")
            self.chroma_client = chromadb.HttpClient(host="localhost", port=8000)

        self.collection = self.chroma_client.get_or_create_collection(name="project_docs")

    def ingest_docs(self):
        """Reads markdown files, splits by paragraph, and stores embeddings in ChromaDB."""
        print(f"Ingesting documentation from {self.docs_path}...")
        
        md_files = glob.glob(os.path.join(self.docs_path, "**/*.md"), recursive=True)
        documents = []
        metadatas = []
        ids = []

        for file_path in md_files:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Simple splitting by double newline to approximate paragraphs
                file_chunks = content.split("\n\n")
                for i, chunk in enumerate(file_chunks):
                    if len(chunk.strip()) > 50:  # Filter out tiny chunks/headers
                        documents.append(chunk.strip())
                        metadatas.append({"source": file_path})
                        ids.append(f"{file_path}_{i}")

        if documents:
            # Generate embeddings
            embeddings = self.model.encode(documents).tolist()
            
            # Upsert to ChromaDB
            self.collection.upsert(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Ingested {len(documents)} chunks to ChromaDB.")
        else:
            print("No documents found to ingest.")

    def query(self, question: str, n_results=3):
        """Finds top N relevant chunks for the question using semantic search."""
        print(f"\nQuerying: '{question}'")
        
        # Embed the query
        query_embeddings = self.model.encode([question]).tolist()
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results
        )
        
        # Display results
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i] if results['metadatas'] else {}
                source = meta.get('source', 'Unknown')
                print(f"\n--- Result {i+1} (Source: {source}) ---")
                print(doc)
                print("-------------------")
        else:
            print("No results found.")
