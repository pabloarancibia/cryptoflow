import uuid
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # 1. Generate unique ID for this request
        request_id = str(uuid.uuid4())

        # 2. Bind it to the global context
        # Any log created after this line will automatically have {"request_id": "..."}
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        # 3. Log the start
        await logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host
        )

        # 4. Process Request
        response = await call_next(request)

        # 5. Log the end
        await logger.info(
            "request_finished",
            status_code=response.status_code
        )

        return response