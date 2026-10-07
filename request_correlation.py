"""Request IDs for HTTP responses, including FastAPI's outer 500 handler."""

from uuid import uuid4

from fastapi import FastAPI, Request
from starlette.datastructures import Headers, MutableHeaders
from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class RequestCorrelationMiddleware:
    """Expose a request-local ID and attach it when response headers are sent."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = Headers(scope=scope).get("x-request-id")
        if request_id is None:
            request_id = str(uuid4())
        scope.setdefault("state", {})["request_id"] = request_id

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)["X-Request-ID"] = request_id
            await send(message)

        await self.app(scope, receive, send_with_request_id)


async def correlated_server_error(request: Request, exc: Exception) -> PlainTextResponse:
    """Preserve the default production 500 body and include the request ID."""
    return PlainTextResponse(
        "Internal Server Error",
        status_code=500,
        headers={"X-Request-ID": request.state.request_id},
    )


def install_request_correlation(app: FastAPI) -> None:
    """Configure an app using FastAPI's default non-debug 500 response."""
    app.add_middleware(RequestCorrelationMiddleware)
    # ServerErrorMiddleware sends unhandled 500s outside application middleware.
    app.add_exception_handler(Exception, correlated_server_error)
