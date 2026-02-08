"""Global dependencies for API routers."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.src.domain.ports.services import TokenService
from backend.src.infrastructure.di import ContainerFactory

security = HTTPBearer()


class CurrentUserIdProvider:
    """Protocol for providing the current authenticated user ID."""

    async def get_user_id(self, auth: HTTPAuthorizationCredentials) -> UUID:
        raise NotImplementedError


class JWTUserIdProvider(CurrentUserIdProvider):
    """Current user provider backed by bearer JWT verification."""

    def __init__(self, token_service: TokenService):
        self.token_service = token_service

    async def get_user_id(
        self,
        auth: HTTPAuthorizationCredentials = Depends(security),
    ) -> UUID:
        payload = await self.token_service.verify_token(auth.credentials)
        if not payload or "user_id" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session",
            )
        try:
            return UUID(str(payload["user_id"]))
        except (TypeError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session",
            ) from exc


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
