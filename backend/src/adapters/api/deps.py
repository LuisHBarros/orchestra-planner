"""Global dependencies for API routers."""

from __future__ import annotations

from uuid import UUID

from backend.src.infrastructure.di import ContainerFactory


class CurrentUserIdProvider:
    """Protocol for providing the current authenticated user ID."""

    async def get_user_id(self) -> UUID:
        raise NotImplementedError


_container_factory: ContainerFactory | None = None
_current_user_id_provider: CurrentUserIdProvider | None = None


def get_container_factory() -> ContainerFactory:
    if _container_factory is None:
        raise RuntimeError("ContainerFactory not initialized")
    return _container_factory


def set_container_factory(factory: ContainerFactory) -> None:
    global _container_factory
    _container_factory = factory


def get_current_user_provider() -> CurrentUserIdProvider | None:
    return _current_user_id_provider


def set_current_user_provider(provider: CurrentUserIdProvider) -> None:
    global _current_user_id_provider
    _current_user_id_provider = provider
