"""
Unit tests for GetPortfolioUseCase

Tests the portfolio retrieval use case with mocked dependencies.
"""

import pytest
from unittest.mock import AsyncMock
from src.application.use_cases.get_portfolio import GetPortfolioUseCase, PortfolioResponse


@pytest.mark.asyncio
async def test_get_portfolio_success():
    """Test successful portfolio retrieval."""
    # Arrange
    mock_uow = AsyncMock()
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None
    
    use_case = GetPortfolioUseCase(uow=mock_uow)
    
    # Act
    result = await use_case.execute()
    
    # Assert
    assert isinstance(result, PortfolioResponse)
    assert "BTC" in result.holdings
    assert "ETH" in result.holdings
    assert "USD" in result.holdings
    assert result.total_assets > 0
    assert result.last_updated is not None


@pytest.mark.asyncio
async def test_get_portfolio_returns_correct_structure():
    """Test that portfolio response has correct structure."""
    # Arrange
    mock_uow = AsyncMock()
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None
    
    use_case = GetPortfolioUseCase(uow=mock_uow)
    
    # Act
    result = await use_case.execute()
    
    # Assert
    assert hasattr(result, 'holdings')
    assert hasattr(result, 'total_assets')
    assert hasattr(result, 'last_updated')
    assert isinstance(result.holdings, dict)
    assert isinstance(result.total_assets, int)
    assert isinstance(result.last_updated, str)


@pytest.mark.asyncio
async def test_get_portfolio_uses_uow():
    """Test that use case properly uses UnitOfWork."""
    # Arrange
    mock_uow = AsyncMock()
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None
    
    use_case = GetPortfolioUseCase(uow=mock_uow)
    
    # Act
    await use_case.execute()
    
    # Assert - verify UoW context manager was used
    mock_uow.__aenter__.assert_called_once()
    mock_uow.__aexit__.assert_called_once()
