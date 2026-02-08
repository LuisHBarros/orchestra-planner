"""Application factory and lifespan configuration."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from backend.src.adapters.api import deps
from backend.src.adapters.api.routers import (
    auth_router,
    invites_router,
    members_router,
    projects_router,
    roles_router,
    tasks_router,
)
from backend.src.adapters.services import (
    EmailNotificationService,
    FernetEncryptionService,
    InMemoryTokenService,
    JWTTokenService,
    MockEmailService,
    MockLLMService,
    MockNotificationService,
    OpenAILLMService,
    SMTPEmailService,
    SimpleEncryptionService,
)
from backend.src.config.settings import get_settings
from backend.src.observability.logging_config import configure_logging
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
from backend.src.domain.services.time_provider import SystemTimeProvider
from backend.src.domain.time import reset_time_provider, set_time_provider
from backend.src.infrastructure.db.session import AsyncSessionLocal
from backend.src.infrastructure.di import ContainerFactory


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
        settings = get_settings()
        configure_logging(settings.log_level)
        time_token = set_time_provider(SystemTimeProvider())

        if settings.email_provider == "mock":
            email_service = MockEmailService()
        else:
            email_service = SMTPEmailService(settings)

        if settings.token_provider == "mock":
            token_service = InMemoryTokenService()
        else:
            token_service = JWTTokenService(settings)

        if settings.encryption_provider == "mock":
            encryption_service = SimpleEncryptionService()
        else:
            encryption_service = FernetEncryptionService(settings.encryption_key or "")

        if settings.llm_provider == "mock":
            llm_service = MockLLMService()
        else:
            llm_service = OpenAILLMService(settings)

        if settings.notification_provider == "mock":
            notification_service = MockNotificationService()
        else:
            notification_service = EmailNotificationService(email_service)

        factory = ContainerFactory(
            session_factory=AsyncSessionLocal,
            email_service=email_service,
            token_service=token_service,
            encryption_service=encryption_service,
            llm_service=llm_service,
            notification_service=notification_service,
            public_base_url=settings.public_base_url,
        )

        deps.set_container_factory(factory)
        deps.set_current_user_provider(deps.JWTUserIdProvider(token_service))

        try:
            yield
        finally:
            reset_time_provider(time_token)

    app = FastAPI(lifespan=lifespan)
    from backend.src.adapters.api.middleware.request_id import RequestIdMiddleware

    app.add_middleware(RequestIdMiddleware)

    _register_exception_handlers(app)

    app.include_router(auth_router)
    app.include_router(projects_router)
    app.include_router(roles_router)
    app.include_router(invites_router)
    app.include_router(members_router)
    app.include_router(tasks_router)

    @app.get("/health")
    async def health():
        readiness = {"db": "ok"}
        status_code = status.HTTP_200_OK
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
        except Exception:
            readiness["db"] = "fail"
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return JSONResponse(
            status_code=status_code,
            content={"liveness": "ok", "readiness": readiness},
        )

    return app
