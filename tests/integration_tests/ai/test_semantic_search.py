import os
import pytest
from src.ai.knowledge_base import ProjectDocumentationDB

@pytest.mark.integration
class TestSemanticSearchIntegration:
    """
    Integration tests for AI Semantic Search.
    Requires: ChromaDB running (e.g., via Docker).
    """

    @pytest.fixture
    def setup_docs(self):
        """Creates dummy documentation for testing."""
        if not os.path.exists("docs"):
            os.makedirs("docs")
            
        test_doc_path = "docs/test_integration_doc.md"
        with open(test_doc_path, "w") as f:
            f.write("# Integration Test Doc\n\nThis is a test document for integration testing.\nVerify semantic search works with real ChromaDB.")
            
        yield test_doc_path
        
        # Cleanup
        if os.path.exists(test_doc_path):
            os.remove(test_doc_path)

    def test_ingestion_and_query(self, setup_docs):
        """
        Verifies end-to-end ingestion and querying with real DB.
        """
        try:
            db = ProjectDocumentationDB(docs_path="docs/")
            
            # 1. Ingest
            db.ingest_docs()
            
            # 2. Query
            # We capture stdout or just rely on no exceptions for now, 
            # ideally we'd refactor query() to return data instead of print it.
            # For this test, valid execution without error is the baseline.
            db.query("integration testing")
            
            # 3. Verify Collection Exists (White-box check)
            assert db.collection.count() > 0
            
        except Exception as e:
            pytest.fail(f"Semantic Search Integration failed: {e}")
