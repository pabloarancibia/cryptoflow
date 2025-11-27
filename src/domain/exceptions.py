
class DomainError(Exception):
    """Base exception for all domain-related errors."""
    pass

class InvalidSymbolError(DomainError):
    """Raised when an asset symbol format is wrong."""
    pass

class NegativePriceError(DomainError):
    """Raised when price or quantity is <= 0."""
    pass

class InsufficientLiquidityError(DomainError):
    """Raised when the market cannot fill the order."""
    pass