"""Database engine and session factory (Async)."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from backend.src.config.settings import AppSettings


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_db(settings: AppSettings) -> None:
    """Initialize engine and session factory exactly once."""
    global _engine, _session_factory
    if _engine is not None and _session_factory is not None:
        return

    if not settings.database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")

    _engine = create_async_engine(
        settings.database_url,
        # Enable SQL logging only when explicitly requested.
        echo=settings.db_echo,
        # pool_pre_ping checks connections before handing them out (prevents 'gone away' errors)
        pool_pre_ping=True,
    )
    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,  # Critical for Async SQLAlchemy
    )


def get_engine() -> AsyncEngine:
    if _engine is None:
        raise RuntimeError("Database engine not initialized. Call init_db() first.")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    if _session_factory is None:
        raise RuntimeError("Session factory not initialized. Call init_db() first.")
    return _session_factory


async def dispose_db() -> None:
    """Dispose active engine and reset db globals (used by tests/lifespan teardown)."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an AsyncSession.

    Session lifecycle dependency.
    Transaction boundaries are managed by UnitOfWork.
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
