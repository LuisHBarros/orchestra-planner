"""Structured logging configuration."""

from __future__ import annotations

import logging

try:
    import structlog
except ModuleNotFoundError:  # pragma: no cover - environment dependent fallback
    structlog = None

from backend.src.observability.logging_context import get_request_id


def _add_request_id(logger, method_name, event_dict):
    event_dict["request_id"] = get_request_id()
    return event_dict


def _add_logger_name(logger, method_name, event_dict):
    event_dict["logger"] = getattr(logger, "name", None)
    return event_dict


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structured JSON logging for app and uvicorn."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(message)s",
    )
    if structlog is None:
        return

    add_logger_name = getattr(structlog.processors, "add_logger_name", _add_logger_name)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            _add_request_id,
            structlog.processors.add_log_level,
            add_logger_name,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.propagate = True
