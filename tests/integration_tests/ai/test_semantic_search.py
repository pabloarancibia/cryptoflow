import pytest
from src.ai.adapters.chroma_adapter import ChromaKBAdapter
from src.ai.domain.models import DocumentChunk
from src.ai.domain.ports import IVectorStore

@pytest.mark.integration
class TestSemanticSearchIntegration:
    """
    Integration tests for AI Semantic Search (Hexagonal).
    Requires: ChromaDB running (e.g., via Docker).
    """

    @pytest.fixture
    def setup_docs(self):
        """Creates dummy data for testing."""
        return [
            DocumentChunk(content="Integration testing is crucial.", metadata={"source": "test"}, id="1"),
            DocumentChunk(content="Hexagonal architecture separates concerns.", metadata={"source": "test"}, id="2")
        ]

    def test_ingestion_and_query(self, setup_docs):
        """
        Verifies end-to-end ingestion and querying with real DB.
        """
        try:
            db: IVectorStore = ChromaKBAdapter(collection_name="test_integration_collection")
            
            # 1. Ingest
            db.ingest(setup_docs)
            
            # 2. Query
            results = db.query("testing architecture")
            
            # 3. Verify
            assert len(results) > 0
            # Check content presence (simple check)
            assert any("Integration" in d.content for d in results) or any("Hexagonal" in d.content for d in results)
            
        except Exception as e:
            pytest.fail(f"Semantic Search Integration failed: {e}")
