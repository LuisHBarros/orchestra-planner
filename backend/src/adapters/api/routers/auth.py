"""Auth API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from backend.src.adapters.api.routers.common import get_container
from backend.src.application.use_cases.auth.request_magic_link import RequestMagicLinkInput
from backend.src.infrastructure.di import Container

router = APIRouter(prefix="/auth", tags=["auth"])


class MagicLinkRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=320)


class VerifyMagicLinkRequest(BaseModel):
    token: str = Field(..., min_length=1)


class VerifyMagicLinkResponse(BaseModel):
    user_id: str
    email: str
    name: str


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
    user = await use_case.execute(request.token)
    return VerifyMagicLinkResponse(user_id=str(user.id), email=user.email, name=user.name)
