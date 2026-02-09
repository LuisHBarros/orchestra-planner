"""Project membership API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel

from backend.src.adapters.api.routers.common import get_container, get_current_user_id
from backend.src.application.use_cases.project_management import (
    FireEmployeeInput,
    ListProjectMembersInput,
    ResignFromProjectInput,
)
from backend.src.infrastructure.di import Container

router = APIRouter(prefix="/projects/{project_id}/members", tags=["members"])


class MemberResponse(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    role_id: UUID
    seniority_level: str
    joined_at: str
    user_name: str
    user_email: str
    role_name: str


class PaginatedMembersResponse(BaseModel):
    items: list[MemberResponse]
    total: int
    limit: int
    offset: int


class UnassignedTasksResponse(BaseModel):
    unassigned_task_ids: list[UUID]


@router.get("", response_model=PaginatedMembersResponse)
async def list_project_members(
    project_id: UUID,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> PaginatedMembersResponse:
    use_case = container.list_project_members_use_case()
    result = await use_case.execute(
        ListProjectMembersInput(
            project_id=project_id,
            requester_id=user_id,
            limit=limit,
            offset=offset,
        )
    )
    return PaginatedMembersResponse(
        items=[
            MemberResponse(
                id=m.id,
                project_id=m.project_id,
                user_id=m.user_id,
                role_id=m.role_id,
                seniority_level=m.seniority_level,
                joined_at=m.joined_at,
                user_name=m.user_name,
                user_email=m.user_email,
                role_name=m.role_name,
            )
            for m in result.items
        ],
        total=result.total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/{user_id}/fire",
    response_model=UnassignedTasksResponse,
    status_code=status.HTTP_200_OK,
)
async def fire_employee(
    project_id: UUID,
    user_id: UUID,
    container: Annotated[Container, Depends(get_container)],
    manager_user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> UnassignedTasksResponse:
    use_case = container.fire_employee_use_case()
    tasks = await use_case.execute(
        FireEmployeeInput(
            project_id=project_id,
            employee_user_id=user_id,
            manager_user_id=manager_user_id,
        )
    )
    return UnassignedTasksResponse(
        unassigned_task_ids=[task.id for task in tasks]
    )


@router.post(
    "/me/resign",
    response_model=UnassignedTasksResponse,
    status_code=status.HTTP_200_OK,
)
async def resign_from_project(
    project_id: UUID,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> UnassignedTasksResponse:
    use_case = container.resign_from_project_use_case()
    tasks = await use_case.execute(
        ResignFromProjectInput(project_id=project_id, user_id=user_id)
    )
    return UnassignedTasksResponse(
        unassigned_task_ids=[task.id for task in tasks]
    )
