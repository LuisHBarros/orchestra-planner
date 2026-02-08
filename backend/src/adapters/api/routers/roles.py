"""Role management API endpoints."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from backend.src.adapters.api.routers.common import get_container, get_current_user_id
from backend.src.application.use_cases.project_management import CreateRoleInput
from backend.src.domain.entities import Role
from backend.src.infrastructure.di import Container

router = APIRouter(prefix="/projects/{project_id}/roles", tags=["roles"])


class CreateRoleRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class RoleResponse(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    created_at: datetime

    @classmethod
    def from_entity(cls, role: Role) -> "RoleResponse":
        return cls(
            id=role.id,
            project_id=role.project_id,
            name=role.name,
            created_at=role.created_at,
        )


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    project_id: UUID,
    request: CreateRoleRequest,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> RoleResponse:
    use_case = container.create_role_use_case()
    role = await use_case.execute(
        CreateRoleInput(
            project_id=project_id,
            requester_id=user_id,
            role_name=request.name,
        )
    )
    return RoleResponse.from_entity(role)
