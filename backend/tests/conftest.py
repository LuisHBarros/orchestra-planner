"""Shared pytest fixtures."""

from __future__ import annotations

import os
import socket

import pytest
from sqlalchemy.engine import make_url


@pytest.fixture(scope="session")
def test_database_url() -> str:
    url = (
        os.getenv("TEST_DATABASE_URL")
        or os.getenv("DATABASE_URL")
        or "postgresql+asyncpg://postgres:postgres@localhost:5432/orchestra_planner"
    )
    parsed = make_url(url)
    if parsed.drivername.startswith("postgresql"):
        host = parsed.host or "localhost"
        port = parsed.port or 5432
        try:
            with socket.create_connection((host, port), timeout=1):
                pass
        except OSError:
            pytest.skip(
                f"Postgres not reachable at {host}:{port}; skipping DB-backed tests"
            )
    return url
