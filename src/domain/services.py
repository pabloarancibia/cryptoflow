# src/domain/services.py
from typing import Set
from src.domain.exceptions import InvalidSymbolError


class SymbolRegistry:
    """
    Domain Service: Acts as the Source of Truth for supported assets.
    """

    # In a real app, these might be loaded from a config file or DB on startup.
    # For now, we hardcode the business rule here.
    _SUPPORTED_CRYPTO: Set[str] = {"BTC", "ETH", "SOL", "XRP", "USDT"}
    _SUPPORTED_FIAT: Set[str] = {"USD", "EUR", "GBP"}

    @classmethod
    def validate(cls, symbol: str) -> None:
        """
        Checks if a symbol is valid. Raises InvalidSymbolError if not.
        """
        upper_sym = symbol.upper()

        is_crypto = upper_sym in cls._SUPPORTED_CRYPTO
        is_fiat = upper_sym in cls._SUPPORTED_FIAT

        if not (is_crypto or is_fiat):
            raise InvalidSymbolError(f"Asset '{upper_sym}' is not supported by CryptoFlow.")