import pytest
from src.ai.knowledge_base import ProjectDocumentationDB
from src.ai.trader_agent import SimulatedAgent

@pytest.mark.integration
class TestAgentDemoIntegration:
    """
    Integration tests for the AI Agent Workflow.
    Migrated from scripts/run_ai_demo.py
    """

    def test_agent_workflow(self, mocker):
        """
        Verifies that the agent can process a prompt and return a response.
        Mocking backend dependencies to avoid real DB calls.
        """
        from unittest.mock import AsyncMock

        # Mock dependencies used in execute_trade
        mock_uow = mocker.patch("src.ai.trader_agent.SqlAlchemyUnitOfWork")
        
        mock_exchange_cls = mocker.patch("src.ai.trader_agent.MockExchangeAdapter")
        mock_exchange_instance = mock_exchange_cls.return_value
        mock_exchange_instance.get_current_price = AsyncMock(return_value=50000.0)

        mock_use_case_cls = mocker.patch("src.ai.trader_agent.PlaceOrderUseCase")
        mock_use_case_instance = mock_use_case_cls.return_value
        mock_use_case_instance.execute = AsyncMock()
        
        # Setup mock return values
        mock_use_case_instance.execute.return_value.order_id = "test-agent-order-123"
        mock_use_case_instance.execute.return_value.price = 50000.0
        
        # 1. RAG Check
        kb = ProjectDocumentationDB(docs_path="docs/")
        assert kb is not None
        
        # 2. Agent Execution
        agent = SimulatedAgent()
        
        prompt = "Please place a SELL order for 1 BTC"
        response = agent.run(prompt)
        
        # Verify response structure
        assert response is not None
        assert "SELL" in str(response)
        assert "BTC" in str(response)
        assert "test-agent-order-123" in str(response)
