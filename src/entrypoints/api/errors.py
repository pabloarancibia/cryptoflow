from fastapi import Request
from fastapi.responses import JSONResponse
from src.domain.exceptions import DomainError, InvalidSymbolError, NegativePriceError


async def domain_exception_handler(request: Request, exc: DomainError):
    """
    Catches any exception inheriting from DomainError and returns JSON.
    """

    # Default status code
    status_code = 400
    error_type = "DomainError"

    # Map specific errors to status codes if needed
    if isinstance(exc, InvalidSymbolError):
        status_code = 422  # Unprocessable Entity
        error_type = "InvalidSymbol"
    elif isinstance(exc, NegativePriceError):
        status_code = 400
        error_type = "NegativePrice"

    return JSONResponse(
        status_code=status_code,
        content={
            "error": error_type,
            "detail": str(exc),
            "path": request.url.path
        },
    )