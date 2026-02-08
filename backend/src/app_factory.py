"""Application factory and lifespan configuration."""

from __future__ import annotations

from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from backend.src.adapters.api.routers import tasks_router
from backend.src.adapters.api.routers import tasks as tasks_router_module
from backend.src.adapters.services import (
    InMemoryTokenService,
    MockEmailService,
    MockLLMService,
    MockNotificationService,
    SimpleEncryptionService,
)
from backend.src.domain.errors import (
    DomainError,
    ManagerRequiredError,
    ProjectAccessDeniedError,
    ProjectNotFoundError,
    TaskNotAssignedError,
    TaskNotFoundError,
    TaskNotOwnedError,
    TaskNotSelectableError,
    WorkloadExceededError,
)
from backend.src.infrastructure.db.session import AsyncSessionLocal
from backend.src.infrastructure.di import ContainerFactory


class DenyAllCurrentUserProvider(tasks_router_module.CurrentUserIdProvider):
    """Auth provider placeholder that forces authentication configuration."""

    async def get_user_id(self) -> UUID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication not configured",
        )


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        status_override = {
            TaskNotFoundError: status.HTTP_404_NOT_FOUND,
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            ManagerRequiredError: status.HTTP_403_FORBIDDEN,
            ProjectAccessDeniedError: status.HTTP_403_FORBIDDEN,
            TaskNotOwnedError: status.HTTP_403_FORBIDDEN,
            TaskNotSelectableError: status.HTTP_422_UNPROCESSABLE_ENTITY,
            WorkloadExceededError: status.HTTP_422_UNPROCESSABLE_ENTITY,
            TaskNotAssignedError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        }

        status_code = status_override.get(type(exc), exc.status)
        return JSONResponse(status_code=status_code, content={"detail": exc.message})

    @app.exception_handler(ValueError)
    async def handle_value_error(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        email_service = MockEmailService()
        token_service = InMemoryTokenService()
        encryption_service = SimpleEncryptionService()
        llm_service = MockLLMService()
        notification_service = MockNotificationService()

        factory = ContainerFactory(
            session_factory=AsyncSessionLocal,
            email_service=email_service,
            token_service=token_service,
            encryption_service=encryption_service,
            llm_service=llm_service,
            notification_service=notification_service,
        )

        tasks_router_module.set_container_factory(factory)
        tasks_router_module.set_current_user_provider(DenyAllCurrentUserProvider())

        yield

    app = FastAPI(lifespan=lifespan)

    _register_exception_handlers(app)

    app.include_router(tasks_router)
    # TODO: include other routers (projects, members, roles, auth, reports) here.

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
