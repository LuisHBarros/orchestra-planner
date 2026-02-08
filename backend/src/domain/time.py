"""Time helpers for deterministic domain behavior."""

from __future__ import annotations

from contextvars import ContextVar
from datetime import datetime

from backend.src.domain.ports.services.time_provider import TimeProvider
from backend.src.domain.services.time_provider import SystemTimeProvider

_time_provider: ContextVar[TimeProvider | None] = ContextVar(
    "time_provider", default=None
)


def _get_provider() -> TimeProvider:
    provider = _time_provider.get()
    if provider is None:
        provider = SystemTimeProvider()
    return provider


def set_time_provider(provider: TimeProvider):
    """Override the time provider (useful for deterministic tests)."""
    return _time_provider.set(provider)


def reset_time_provider(token=None) -> None:
    """Reset to the default system time provider."""
    if token is not None:
        _time_provider.reset(token)
        return
    _time_provider.set(None)


def utcnow() -> datetime:
    """Return current UTC time via the configured provider."""
    return _get_provider().now()
