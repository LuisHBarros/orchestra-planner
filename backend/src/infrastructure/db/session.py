"""Database engine and session factory (Async)."""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def _get_database_url() -> str:
    """Retrieve and validate the database URL."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    return database_url


def create_db_engine():
    """Create a SQLAlchemy Async engine."""
    return create_async_engine(
        _get_database_url(),
        # echo=True is good for debugging, turn off in production
        echo=True,
        # pool_pre_ping checks connections before handing them out (prevents 'gone away' errors)
        pool_pre_ping=True,
    )


# Initialize the Async Engine
engine = create_db_engine()

# Create the Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,  # Critical for Async SQLAlchemy
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an AsyncSession.

    Ensures the session is closed even if an error occurs.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
