import pytest
from unittest.mock import MagicMock, patch, mock_open
from src.ai.knowledge_base import ProjectDocumentationDB
from tests.factories.ai_factories import DocumentChunkFactory
import chromadb

class TestProjectDocumentationDB:
    
    @pytest.fixture
    def mock_chroma_client(self, mocker):
        return mocker.patch("chromadb.HttpClient")

    @pytest.fixture
    def mock_sentence_transformer(self, mocker):
        # Patch the class itself to return a mock instance
        mock_class = mocker.patch("src.ai.knowledge_base.SentenceTransformer")
        mock_instance = mock_class.return_value
        # Mock encode to return a dummy embedding list
        mock_instance.encode.return_value.tolist.return_value = [[0.1, 0.2, 0.3]]
        return mock_instance

    @pytest.fixture
    def db_instance(self, mock_chroma_client, mock_sentence_transformer):
        # We also need to mock valid connection to avoid constructor failing
        mock_chroma_client.return_value.heartbeat.return_value = True
        return ProjectDocumentationDB(docs_path="dummy_docs/")

    def test_initialization_localhost(self, mocker, mock_sentence_transformer):
        """Test that initialization attempts to connect to localhost first."""
        mock_params = mocker.patch("chromadb.HttpClient")
        mock_params.return_value.heartbeat.return_value = True
        
        db = ProjectDocumentationDB()
        
        mock_params.assert_called_with(host="localhost", port=8001)
        assert db.chroma_client == mock_params.return_value

    def test_initialization_fallback(self, mocker, mock_sentence_transformer):
        """Test fallback to chroma:8000 if localhost fails."""
        mock_http = mocker.patch("chromadb.HttpClient")
        
        # side_effect: first call raises Exception, second call returns mock
        mock_client_instance = MagicMock()
        mock_client_instance.heartbeat.return_value = True
        
        def side_effect(host, port):
            if host == "localhost":
                raise Exception("Connection Refused")
            return mock_client_instance

        mock_http.side_effect = side_effect
        
        db = ProjectDocumentationDB()
        
        # Verify it tried localhost, then chroma
        assert mock_http.call_count == 2
        mock_http.assert_any_call(host="localhost", port=8001)
        mock_http.assert_any_call(host="chroma", port=8000)
        assert db.chroma_client == mock_client_instance

    def test_ingest_docs(self, db_instance, mocker):
        """Test document ingestion mock flow."""
        # Mock glob and open
        mocker.patch("glob.glob", return_value=["dummy_docs/test.md"])
        
        # Chunk must be > 50 chars to be ingested
        chunk_data = "This is a test chunk. It has enough content to be ingested by the system. " * 3
        mock_file = mock_open(read_data=chunk_data)
        mocker.patch("builtins.open", mock_file)
        
        # Mock collection
        mock_collection = db_instance.collection
        
        db_instance.ingest_docs()
        
        # Verify encode was called
        db_instance.model.encode.assert_called()
        
        # Verify upsert
        mock_collection.upsert.assert_called_once()
        call_args = mock_collection.upsert.call_args[1]
        assert len(call_args['documents']) == 1
        assert call_args['ids'][0].startswith("dummy_docs/test.md")

    def test_query(self, db_instance):
        """Test querying the database."""
        # Setup mock return for query
        mock_collection = db_instance.collection
        mock_collection.query.return_value = {
            'documents': [['Result chunk 1', 'Result chunk 2']],
            'metadatas': [[{'source': 'doc1'}, {'source': 'doc2'}]]
        }
        
        from tests.factories.ai_factories import fake
        test_question = fake.sentence()
        
        db_instance.query(test_question)
        
        # Verify encode call for query
        db_instance.model.encode.assert_called_with([test_question])
        
        # Verify collection query
        mock_collection.query.assert_called_once()
