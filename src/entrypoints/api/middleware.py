import uuid
import structlog
from starlette.types import ASGIApp, Receive, Scope, Send

logger = structlog.get_logger()

class RequestLogMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 1. Setup Context (Same as before)
        request_id = str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        # 2. Extract Details from Scope (No Request object needed)
        client = scope.get("client")
        client_ip = client[0] if client else "unknown"
        method = scope.get("method")
        path = scope.get("path")

        logger.info(
            "request_started",
            method=method,
            path=path,
            client_ip=client_ip
        )

        # 3. Wrapper to intercept the status code
        # In Pure ASGI, we don't get a "Response" object returned.
        # We catch the 'http.response.start' message as it flies back out.
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                logger.info(
                    "request_finished",
                    status_code=status_code
                )
            await send(message)

        # 4. Process Request (Await the app directly, no background task)
        await self.app(scope, receive, send_wrapper)