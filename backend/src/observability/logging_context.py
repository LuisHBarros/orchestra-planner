"""Context management for structured logging."""

from __future__ import annotations

from contextvars import ContextVar

_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_request_id(value: str) -> object:
    """Set request_id in context and return token for reset."""
    return _request_id.set(value)


def reset_request_id(token: object) -> None:
    """Reset request_id context using token."""
    _request_id.reset(token)


def get_request_id() -> str | None:
    """Get current request_id from context."""
    return _request_id.get()
