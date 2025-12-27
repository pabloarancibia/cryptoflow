
import sys
import os

# Add src to path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.ai.knowledge_base import ProjectDocumentationDB
except ImportError as e:
    print(f"Error importing knowledge_base: {e}")
    sys.exit(1)

def main():
    print("Initializing KnowledgeBase...")
    try:
        db = ProjectDocumentationDB(docs_path="docs/")
        
        # Create a dummy doc for testing if no docs exist or to ensure we have something
        test_doc_path = "docs/test_doc.md"
        if not os.path.exists("docs"):
            os.makedirs("docs")
        with open(test_doc_path, "w") as f:
            f.write("# Test Document\n\nThis is a test document about the Semantic Search feature.\nIt uses ChromaDB and SentenceTransformers.")
            
        print("Ingesting documentation...")
        db.ingest_docs()
        
        print("\nTesting Query: 'What is Semantic Search?'")
        db.query("What is Semantic Search?")
        
        # Clean up dummy doc
        if os.path.exists(test_doc_path):
            os.remove(test_doc_path)
            
        print("\nTest Complete!")
        
    except Exception as e:
        print(f"Test Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
