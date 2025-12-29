import pytest
from src.ai.domain.ports import ILLMProvider
from src.ai.domain.models import ToolCall
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
        # Mock LLM to return a ToolCall for trading
        mock_llm = mocker.Mock(spec=ILLMProvider)
        mock_tool_call = ToolCall(
            name="execute_trade",
            arguments={"symbol": "BTC", "side": "buy", "quantity": 1.0}
        )
        mock_llm.generate_with_tools.return_value = mock_tool_call
        
        # Real Tool Adapter (has internal mock logic)
        tools = TradingToolAdapter()
        
        # Agent Execution
        agent = TraderAgent(llm_provider=mock_llm, trading_tool=tools)
        
        prompt = "Please place a BUY order for 1 BTC"
        response = agent.run(prompt)
        
        # Verify response structure
        assert response is not None
        assert response.tool_used == "execute_trade"
        assert response.tool_result["symbol"] == "BTC"
        assert response.tool_result["side"] == "buy"
        assert response.tool_result["status"] == "filled"
