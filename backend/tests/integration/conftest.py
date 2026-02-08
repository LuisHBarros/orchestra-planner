"""Integration test fixtures backed by Postgres."""

from __future__ import annotations

import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.src.infrastructure.db.base import Base
from backend.src.infrastructure.db import models as _models  # noqa: F401


@pytest_asyncio.fixture(scope="session")
async def integration_engine(test_database_url: str):
    engine = create_async_engine(test_database_url, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture
async def db_session(integration_engine) -> AsyncSession:
    session_factory = async_sessionmaker(
        bind=integration_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        tx = await session.begin()
        try:
            yield session
        finally:
            await tx.rollback()
            await session.close()


@pytest.fixture(scope="session", autouse=True)
def _set_database_url_for_app(test_database_url: str):
    os.environ.setdefault("DATABASE_URL", test_database_url)


@pytest_asyncio.fixture
async def api_client(test_database_url: str, monkeypatch):
    from backend.src.app_factory import create_app
    from backend.src.config.settings import get_settings

    monkeypatch.setenv("DATABASE_URL", test_database_url)
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setenv("EMAIL_PROVIDER", "mock")
    monkeypatch.setenv("TOKEN_PROVIDER", "mock")
    monkeypatch.setenv("ENCRYPTION_PROVIDER", "mock")
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("NOTIFICATION_PROVIDER", "mock")
    get_settings.cache_clear()

    app = create_app()
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            yield client
