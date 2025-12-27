import pytest
from src.ai.adapters.llm_adapter import LLMAdapter
from src.ai.adapters.trading_tools_adapter import TradingToolAdapter
from src.ai.application.agent_service import TraderAgent

@pytest.mark.integration
class TestAgentDemoIntegration:
    """
    Integration tests for the AI Agent Workflow (Hexagonal Architecture).
    Migrated from scripts/run_ai_demo.py
    """

    def test_agent_workflow(self, mocker):
        """
        Verifies that the agent can process a prompt and return a response.
        Mocking backend dependencies to avoid real DB calls.
        """
        # Mock LLM to return a predictable JSON for trading
        # checking if we need to mock LLMAdapter provided it acts as port
        
        mock_llm = mocker.Mock(spec=LLMAdapter)
        mock_llm.generate_text.return_value = '{"tool": "execute_trade", "symbol": "BTC", "side": "buy", "quantity": 1.0}'
        
        # Real or Mocked Tool Adapter
        # Using real adapter but internal methods are mocked if needed
        # For now, TradingToolAdapter has internal mock logic, so safe to use directly
        tools = TradingToolAdapter()
        
        # 2. Agent Execution
        agent = TraderAgent(llm_provider=mock_llm, trading_tool=tools)
        
        prompt = "Please place a BUY order for 1 BTC"
        response = agent.run(prompt)
        
        # Verify response structure
        assert response is not None
        assert response.tool_used == "execute_trade"
        assert response.tool_result["symbol"] == "BTC"
        assert response.tool_result["side"] == "buy"
        assert response.tool_result["status"] == "filled"
