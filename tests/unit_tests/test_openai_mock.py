import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from unittest.mock import MagicMock, patch
from src.ai.adapters.llm.openai import OpenAIAdapter
from src.ai.domain.models import ToolCall

class TestOpenAIAdapter(unittest.TestCase):
    def setUp(self):
        self.api_key = "fake-key"
        with patch("openai.OpenAI") as MockClient:
            self.adapter = OpenAIAdapter(api_key=self.api_key)
            self.mock_client = self.adapter.client

    def test_generate_with_tools_tool_call(self):
        # Mock the response
        mock_completion = MagicMock()
        mock_message = MagicMock()
        mock_tool_call = MagicMock()
        
        mock_tool_call.function.name = "execute_trade"
        mock_tool_call.function.arguments = '{"symbol": "BTC", "side": "buy", "quantity": 1.5}'
        
        mock_message.tool_calls = [mock_tool_call]
        mock_message.content = None
        
        mock_completion.choices = [MagicMock(message=mock_message)]
        self.mock_client.chat.completions.create.return_value = mock_completion
        
        # Call the method
        tools = [{"name": "execute_trade", "parameters": {}}]
        result = self.adapter.generate_with_tools("Buy 1.5 BTC", tools)
        
        # Verify
        self.assertIsInstance(result, ToolCall)
        self.assertEqual(result.name, "execute_trade")
        self.assertEqual(result.arguments["symbol"], "BTC")
        self.assertEqual(result.arguments["quantity"], 1.5)
        
        # Verify arguments passed to OpenAI
        args, kwargs = self.mock_client.chat.completions.create.call_args
        self.assertEqual(kwargs["model"], "gpt-4o-mini")
        self.assertEqual(kwargs["tools"][0]["type"], "function")

    def test_generate_with_tools_text_response(self):
        # Mock the response
        mock_completion = MagicMock()
        mock_message = MagicMock()
        
        mock_message.tool_calls = None
        mock_message.content = "Just chatting."
        
        mock_completion.choices = [MagicMock(message=mock_message)]
        self.mock_client.chat.completions.create.return_value = mock_completion
        
        # Call the method
        tools = [{"name": "execute_trade", "parameters": {}}]
        result = self.adapter.generate_with_tools("Hello", tools)
        
        # Verify
        self.assertEqual(result, "Just chatting.")

if __name__ == "__main__":
    unittest.main()
