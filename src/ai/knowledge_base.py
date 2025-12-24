import os
import glob
from rank_bm25 import BM25Okapi

class ProjectDocumentationDB:
    def __init__(self, docs_path="docs/"):
        self.docs_path = docs_path
        self.chunks = []
        self.bm25 = None
        self.is_ingested = False

    def ingest_docs(self):
        """Reads markdown files, splits by paragraph, and builds BM25 index."""
        print(f"Ingesting documentation from {self.docs_path}...")
        
        md_files = glob.glob(os.path.join(self.docs_path, "**/*.md"), recursive=True)
        all_chunks = []

        for file_path in md_files:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Simple splitting by double newline to approximate paragraphs
                # Also adding filename for context
                file_chunks = content.split("\n\n")
                for chunk in file_chunks:
                    if len(chunk.strip()) > 50:  # Filter out tiny chunks/headers
                        all_chunks.append(f"Source: {file_path}\nContent:\n{chunk.strip()}")

        self.chunks = all_chunks
        
        # Tokenize for BM25
        tokenized_corpus = [doc.split(" ") for doc in self.chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)
        self.is_ingested = True
        print(f"Ingested {len(self.chunks)} chunks.")

    def query(self, question: str, n_results=3):
        """Finds top N relevant chunks for the question."""
        if not self.is_ingested:
            print("Database not ingested. Call ingest_docs() first.")
            return

        print(f"\nQuerying: '{question}'")
        tokenized_query = question.split(" ")
        
        # Get top N results
        results = self.bm25.get_top_n(tokenized_query, self.chunks, n=n_results)
        
        for i, res in enumerate(results):
            print(f"\n--- Result {i+1} ---")
            print(res)
            print("-------------------")
