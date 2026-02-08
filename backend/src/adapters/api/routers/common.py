"""Shared dependencies for API routers."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.adapters.api import deps
from backend.src.infrastructure.db.session import get_db
from backend.src.infrastructure.di import Container, ContainerFactory


async def get_container(
    session: Annotated[AsyncSession, Depends(get_db)],
    factory: Annotated[ContainerFactory, Depends(deps.get_container_factory)],
) -> Container:
    """FastAPI dependency for obtaining a DI container."""
    return factory.create(session)


async def get_current_user_id() -> UUID:
    """Get the current authenticated user's ID."""
    provider = deps.get_current_user_provider()
    if provider is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication not configured",
        )
    return await provider.get_user_id()
