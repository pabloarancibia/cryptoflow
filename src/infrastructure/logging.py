import logging
import sys
import structlog


def configure_logging():
    """
    Configures structlog to output JSON logs.
    Includes timestamps, log levels, and context variables (like request_id).
    """

    # 1. shared processors (formatting steps)
    processors = [
        structlog.contextvars.merge_contextvars,  # Add request_id if available
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,  # Print full trace on error
        structlog.processors.JSONRenderer()  # OUTPUT AS JSON
    ]

    # 2. Configure structlog
    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # 3. (Optional) Redirect standard library logging to structlog
    # This captures logs from Uvicorn/FastAPI and formats them as JSON too.
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )