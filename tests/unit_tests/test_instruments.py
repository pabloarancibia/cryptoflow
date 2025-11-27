import pytest
from src.domain.entities import CryptoAsset, FiatCurrency
from src.domain.exceptions import InvalidSymbolError


class TestFinancialInstruments:
    """
    Grouping all Financial Instrument tests in one class.
    Pytest will automatically discover this class because it starts with 'Test'.
    """

    def setup_method(self):
        """
        Runs BEFORE every test method in this class.
        Useful for resetting state or creating fresh objects.
        """
        self.btc = CryptoAsset("BTC")
        self.usd = FiatCurrency("USD")

    def test_validation_rules(self):
        """Test that symbols are validated correctly."""
        # Valid cases
        assert self.btc.validate_symbol() is True
        assert self.usd.validate_symbol() is True

        # Invalid cases (using context manager for exceptions)
        with pytest.raises(InvalidSymbolError):
            # Too long for Fiat (must be 3 chars)
            FiatCurrency("USDT")

    def test_quantization_logic(self):
        """Test decimal precision logic."""
        raw_amount = 1.55555555

        # Access the objects created in setup_method using 'self'
        assert self.btc.quantize(raw_amount) == 1.55555555  # Keeps 8 decimals
        assert self.usd.quantize(raw_amount) == 1.56  # Rounds to 2 decimals

    def test_fee_calculation(self):
        """Test fee structures."""
        qty = 10.0
        price = 200.0

        # BTC: 0.1% of volume (10 * 200 = 2000) -> Fee is 2.0
        expected_btc_fee = (qty * price) * 0.001
        assert self.btc.calculate_fee(qty, price) == expected_btc_fee

        # USD: Flat fee regardless of volume
        assert self.usd.calculate_fee(qty, price) == 1.00

    def test_polymorphism_in_collection(self):
        """Test iterating over different types."""
        portfolio = [self.btc, self.usd]

        results = []
        for asset in portfolio:
            # Polymorphism: calling same method name, getting different logic
            results.append(asset.quantize(1.009))

        # BTC (1.009) vs USD (1.01)
        assert results == [1.009, 1.01]