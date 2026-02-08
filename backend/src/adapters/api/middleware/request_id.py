"""Middleware for request correlation IDs."""

from __future__ import annotations

from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from backend.src.observability.logging_context import reset_request_id, set_request_id


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Ensure every request has a correlation ID."""

    header_name = "X-Request-Id"

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get(self.header_name) or str(uuid4())
        token = set_request_id(request_id)
        try:
            response = await call_next(request)
        finally:
            reset_request_id(token)
        response.headers[self.header_name] = request_id
        return response
