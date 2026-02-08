"""Invitation API endpoints."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from backend.src.adapters.api.routers.common import get_container, get_current_user_id
from backend.src.application.use_cases.invitations import AcceptInviteInput, CreateInviteInput
from backend.src.domain.entities import ProjectInvite, ProjectMember, SeniorityLevel
from backend.src.infrastructure.di import Container

router = APIRouter(tags=["invites"])


class CreateInviteRequest(BaseModel):
    role_id: UUID


class InviteResponse(BaseModel):
    token: str
    project_id: UUID
    role_id: UUID
    created_by: UUID
    status: str
    expires_at: datetime
    created_at: datetime

    @classmethod
    def from_entity(cls, invite: ProjectInvite) -> "InviteResponse":
        return cls(
            token=invite.token,
            project_id=invite.project_id,
            role_id=invite.role_id,
            created_by=invite.created_by,
            status=invite.status.value,
            expires_at=invite.expires_at,
            created_at=invite.created_at,
        )


class CreateInviteResponse(BaseModel):
    invite: InviteResponse
    invite_url: str


class AcceptInviteRequest(BaseModel):
    seniority_level: SeniorityLevel = SeniorityLevel.MID


class MemberResponse(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    role_id: UUID
    seniority_level: SeniorityLevel
    joined_at: datetime

    @classmethod
    def from_entity(cls, member: ProjectMember) -> "MemberResponse":
        return cls(
            id=member.id,
            project_id=member.project_id,
            user_id=member.user_id,
            role_id=member.role_id,
            seniority_level=member.seniority_level,
            joined_at=member.joined_at,
        )


@router.post(
    "/projects/{project_id}/invites",
    response_model=CreateInviteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_invite(
    project_id: UUID,
    request: CreateInviteRequest,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> CreateInviteResponse:
    use_case = container.create_invite_use_case()
    result = await use_case.execute(
        CreateInviteInput(
            project_id=project_id,
            role_id=request.role_id,
            requester_id=user_id,
        )
    )
    return CreateInviteResponse(
        invite=InviteResponse.from_entity(result.invite),
        invite_url=result.invite_url,
    )


@router.post(
    "/invites/{token}/accept",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def accept_invite(
    token: str,
    request: AcceptInviteRequest,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> MemberResponse:
    use_case = container.accept_invite_use_case()
    result = await use_case.execute(
        AcceptInviteInput(
            token=token,
            user_id=user_id,
            seniority_level=request.seniority_level,
        )
    )
    return MemberResponse.from_entity(result.member)
