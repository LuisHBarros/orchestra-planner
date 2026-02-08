"""Project membership API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from backend.src.adapters.api.routers.common import get_container, get_current_user_id
from backend.src.application.use_cases.project_management import (
    FireEmployeeInput,
    ResignFromProjectInput,
)
from backend.src.infrastructure.di import Container

router = APIRouter(prefix="/projects/{project_id}/members", tags=["members"])


class UnassignedTasksResponse(BaseModel):
    unassigned_task_ids: list[UUID]


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
