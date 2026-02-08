"""Auth API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from backend.src.adapters.api.routers.common import get_container
from backend.src.adapters.api import deps
from backend.src.application.use_cases.auth.request_magic_link import RequestMagicLinkInput
from backend.src.config.settings import get_settings
from backend.src.infrastructure.di import Container
from backend.src.adapters.services import MockEmailService

router = APIRouter(prefix="/auth", tags=["auth"])


class MagicLinkRequest(BaseModel):
    email: EmailStr = Field(..., description="The user's email address")


class VerifyMagicLinkRequest(BaseModel):
    token: str = Field(..., min_length=1)


class VerifyMagicLinkResponse(BaseModel):
    user_id: UUID
    email: str
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class DebugMagicLinkResponse(BaseModel):
    recipients: list[str]
    subject: str
    body_text: str
    body_html: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


@router.post("/magic-link", status_code=status.HTTP_204_NO_CONTENT)
async def request_magic_link(
    request: MagicLinkRequest,
    container: Annotated[Container, Depends(get_container)],
) -> None:
    use_case = container.request_magic_link_use_case()
    await use_case.execute(RequestMagicLinkInput(email=request.email))


@router.post("/verify", response_model=VerifyMagicLinkResponse)
async def verify_magic_link(
    request: VerifyMagicLinkRequest,
    container: Annotated[Container, Depends(get_container)],
) -> VerifyMagicLinkResponse:
    use_case = container.verify_magic_link_use_case()
    result = await use_case.execute(request.token)
    return VerifyMagicLinkResponse(
        user_id=result.user.id,
        email=result.user.email,
        access_token=result.tokens.access_token,
        refresh_token=result.tokens.refresh_token,
        token_type=result.tokens.token_type,
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    container: Annotated[Container, Depends(get_container)],
) -> RefreshTokenResponse:
    tokens = await container.services.token.refresh_token(request.refresh_token)
    if tokens is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    return RefreshTokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
    )


@router.post("/revoke", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_token(
    request: RefreshTokenRequest,
    container: Annotated[Container, Depends(get_container)],
) -> None:
    await container.services.token.revoke_token(request.refresh_token)


@router.get("/debug/last-magic-link", response_model=DebugMagicLinkResponse)
async def get_last_magic_link() -> DebugMagicLinkResponse:
    settings = get_settings()
    if settings.app_env.lower() != "local":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    if settings.email_provider.lower() != "mock":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="EMAIL_PROVIDER must be set to mock",
        )

    factory = deps.get_container_factory()
    email_service = factory.get_email_service()
    if not isinstance(email_service, MockEmailService):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MockEmailService not configured",
        )

    if not email_service.sent_messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No magic link sent yet",
        )

    message = email_service.sent_messages[-1]
    return DebugMagicLinkResponse(
        recipients=message.recipients,
        subject=message.subject,
        body_text=message.body_text,
        body_html=message.body_html,
    )
