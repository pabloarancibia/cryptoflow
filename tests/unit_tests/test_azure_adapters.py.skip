import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from unittest.mock import MagicMock, patch, Mock
from src.ai.domain.models import DocumentChunk, ToolCall


class TestAzureSearchAdapter(unittest.TestCase):
    """Unit tests for Azure AI Search adapter."""
    
    @patch('src.ai.adapters.azure.search_adapter.SearchClient')
    @patch('src.ai.adapters.azure.search_adapter.SearchIndexClient')
    @patch('src.ai.adapters.azure.search_adapter.SentenceTransformer')
    def setUp(self, mock_transformer, mock_index_client, mock_search_client):
        """Set up test fixtures."""
        os.environ['AZURE_SEARCH_ENDPOINT'] = 'https://test.search.windows.net'
        os.environ['AZURE_SEARCH_API_KEY'] = 'test-key'
        
        # Mock the sentence transformer
        self.mock_model = MagicMock()
        self.mock_model.encode.return_value = [0.1] * 384  # Mock embedding
        mock_transformer.return_value = self.mock_model
        
        # Mock index client
        self.mock_index_client = MagicMock()
        mock_index_client.return_value = self.mock_index_client
        
        # Mock search client
        self.mock_search_client = MagicMock()
        mock_search_client.return_value = self.mock_search_client
        
        from src.ai.adapters.azure.search_adapter import AzureSearchAdapter
        self.adapter = AzureSearchAdapter()
    
    def test_ingest_documents(self):
        """Test document ingestion."""
        chunks = [
            DocumentChunk(
                id="test-1",
                content="Test content",
                metadata={"source": "test.md"}
            )
        ]
        
        self.adapter.ingest(chunks)
        
        # Verify upload was called
        self.mock_search_client.upload_documents.assert_called_once()
        
        # Verify document structure
        call_args = self.mock_search_client.upload_documents.call_args
        docs = call_args.kwargs['documents']
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]['id'], 'test-1')
        self.assertEqual(docs[0]['content'], 'Test content')
    
    def test_query_documents(self):
        """Test document querying."""
        # Mock search results
        mock_result = {
            'id': 'test-1',
            'content': 'Test content',
            'metadata': '{"source": "test.md"}'
        }
        self.mock_search_client.search.return_value = [mock_result]
        
        results = self.adapter.query("test query", n_results=5)
        
        # Verify search was called
        self.mock_search_client.search.assert_called_once()
        
        # Verify results
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], DocumentChunk)
        self.assertEqual(results[0].id, 'test-1')
        self.assertEqual(results[0].content, 'Test content')


class TestAzureSemanticKernelAdapter(unittest.TestCase):
    """Unit tests for Azure Semantic Kernel adapter."""
    
    @patch('src.ai.adapters.azure.llm_adapter.Kernel')
    @patch('src.ai.adapters.azure.llm_adapter.AzureChatCompletion')
    def setUp(self, mock_chat_completion, mock_kernel):
        """Set up test fixtures."""
        os.environ['AZURE_OPENAI_ENDPOINT'] = 'https://test.openai.azure.com/'
        os.environ['AZURE_OPENAI_API_KEY'] = 'test-key'
        os.environ['AZURE_OPENAI_DEPLOYMENT_NAME'] = 'gpt-4o'
        
        # Mock kernel
        self.mock_kernel = MagicMock()
        mock_kernel.return_value = self.mock_kernel
        
        # Mock chat service
        self.mock_chat_service = MagicMock()
        self.mock_kernel.get_service.return_value = self.mock_chat_service
        
        from src.ai.adapters.azure.llm_adapter import AzureSemanticKernelAdapter
        self.adapter = AzureSemanticKernelAdapter()
    
    def test_generate_text(self):
        """Test text generation."""
        # Mock response
        mock_response = MagicMock()
        mock_response.__str__ = lambda x: "Generated text"
        self.mock_chat_service.get_chat_message_content.return_value = mock_response
        
        result = self.adapter.generate_text("Test prompt")
        
        self.assertEqual(result, "Generated text")
        self.mock_chat_service.get_chat_message_content.assert_called_once()
    
    def test_generate_with_tools_text_response(self):
        """Test tool calling with text response."""
        # Mock response without function call
        mock_response = MagicMock()
        mock_response.__str__ = lambda x: "Just text"
        mock_response.items = []
        self.mock_chat_service.get_chat_message_content.return_value = mock_response
        
        tools = [{
            "name": "execute_trade",
            "description": "Execute a trade",
            "parameters": {}
        }]
        
        result = self.adapter.generate_with_tools("Hello", tools)
        
        self.assertEqual(result, "Just text")
    
    def test_generate_with_tools_function_call(self):
        """Test tool calling with function call."""
        # Mock response with function call
        mock_item = MagicMock()
        mock_item.function_name = "execute_trade"
        mock_item.arguments = '{"symbol": "BTC", "side": "buy", "quantity": 1.5}'
        
        mock_response = MagicMock()
        mock_response.items = [mock_item]
        self.mock_chat_service.get_chat_message_content.return_value = mock_response
        
        tools = [{
            "name": "execute_trade",
            "description": "Execute a trade",
            "parameters": {}
        }]
        
        result = self.adapter.generate_with_tools("Buy 1.5 BTC", tools)
        
        self.assertIsInstance(result, ToolCall)
        self.assertEqual(result.name, "execute_trade")
        self.assertEqual(result.arguments["symbol"], "BTC")


if __name__ == "__main__":
    unittest.main()
