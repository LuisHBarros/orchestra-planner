"""Task management API endpoints."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.src.application.use_cases.task_management import (
    AbandonTaskInput,
    AddDependencyInput,
    AddTaskReportInput,
    CancelTaskInput,
    CompleteTaskInput,
    CreateTaskInput,
    DeleteTaskInput,
    RemoveDependencyInput,
    RemoveFromTaskInput,
    SelectTaskInput,
)
from backend.src.domain.entities import Task, TaskLog
from backend.src.adapters.api.routers.common import get_container, get_current_user_id
from backend.src.infrastructure.di import Container

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])


# --- Pydantic Schemas ---


class CreateTaskRequest(BaseModel):
    """Request body for creating a task."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="", max_length=5000)
    difficulty_points: int | None = Field(default=None, ge=0, le=100)
    required_role_id: UUID | None = None


class SelectTaskRequest(BaseModel):
    """Request body for selecting a task (empty, user comes from auth)."""

    pass


class AbandonTaskRequest(BaseModel):
    """Request body for abandoning a task."""

    reason: str = Field(..., min_length=1, max_length=1000)


class AddReportRequest(BaseModel):
    """Request body for adding a progress report."""

    report_text: str = Field(..., min_length=1, max_length=5000)


class AddDependencyRequest(BaseModel):
    blocking_task_id: UUID


class TaskResponse(BaseModel):
    """Response schema for a task."""

    id: UUID
    project_id: UUID
    title: str
    description: str
    difficulty_points: int | None
    status: str
    assignee_id: UUID | None
    required_role_id: UUID | None
    progress_percent: int
    expected_start_date: datetime | None
    expected_end_date: datetime | None
    actual_end_date: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, task: Task) -> "TaskResponse":
        """Create response from domain entity."""
        return cls(
            id=task.id,
            project_id=task.project_id,
            title=task.title,
            description=task.description,
            difficulty_points=task.difficulty_points,
            status=task.status.value,
            assignee_id=task.assignee_id,
            required_role_id=task.required_role_id,
            progress_percent=task.progress_percent,
            expected_start_date=task.expected_start_date,
            expected_end_date=task.expected_end_date,
            actual_end_date=task.actual_end_date,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )


class TaskLogResponse(BaseModel):
    """Response schema for a task log entry."""

    id: UUID
    task_id: UUID
    author_id: UUID
    log_type: str
    content: str
    created_at: datetime

    @classmethod
    def from_entity(cls, log: TaskLog) -> "TaskLogResponse":
        """Create response from domain entity."""
        return cls(
            id=log.id,
            task_id=log.task_id,
            author_id=log.author_id,
            log_type=log.log_type.value,
            content=log.content,
            created_at=log.created_at,
        )


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str
    rule_id: str | None = None


class PaginatedTasksResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    limit: int
    offset: int


# --- Endpoints ---


@router.get("", response_model=PaginatedTasksResponse)
async def list_tasks(
    project_id: UUID,
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> PaginatedTasksResponse:
    async with container.uow:
        project = await container.uow.project_repository.find_by_id(project_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found",
            )

        member = await container.uow.project_member_repository.find_by_project_and_user(
            project_id, user_id
        )
        if member is None and not project.is_manager(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Project access denied",
            )

        items = await container.uow.task_repository.list_by_project(
            project_id, limit=limit, offset=offset
        )
        total = await container.uow.task_repository.count_by_project(project_id)

    return PaginatedTasksResponse(
        items=[TaskResponse.from_entity(task) for task in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        403: {"model": ErrorResponse, "description": "Not authorized (not manager)"},
        404: {"model": ErrorResponse, "description": "Project not found"},
    },
)
async def create_task(
    project_id: UUID,
    request: CreateTaskRequest,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> TaskResponse:
    """
    Create a new task in a project.

    BR-TASK-001: Only the Manager can create tasks.
    """
    use_case = container.create_task_use_case()

    task = await use_case.execute(
        CreateTaskInput(
            project_id=project_id,
            requester_id=user_id,
            title=request.title,
            description=request.description,
            difficulty_points=request.difficulty_points,
            required_role_id=request.required_role_id,
        )
    )
    return TaskResponse.from_entity(task)


@router.post(
    "/{task_id}/select",
    response_model=TaskResponse,
    responses={
        403: {"model": ErrorResponse, "description": "Not authorized"},
        404: {"model": ErrorResponse, "description": "Task or project not found"},
        422: {"model": ErrorResponse, "description": "Task not selectable"},
    },
)
async def select_task(
    project_id: UUID,
    task_id: UUID,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> TaskResponse:
    """
    Select (self-assign) a task.

    BR-ASSIGN-002: Employees must self-select tasks.
    BR-ASSIGN-003: Cannot select if workload would become Impossible.
    BR-TASK-004: Cannot select if difficulty is not set.
    """
    use_case = container.select_task_use_case()

    task = await use_case.execute(
        SelectTaskInput(
            project_id=project_id,
            task_id=task_id,
            user_id=user_id,
        )
    )
    return TaskResponse.from_entity(task)


@router.post(
    "/{task_id}/complete",
    response_model=TaskResponse,
    responses={
        403: {"model": ErrorResponse, "description": "Not task owner"},
        404: {"model": ErrorResponse, "description": "Task not found"},
        400: {"model": ErrorResponse, "description": "Task not in Doing status"},
    },
)
async def complete_task(
    project_id: UUID,
    task_id: UUID,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> TaskResponse:
    """
    Complete a task that you are working on.

    Only the assigned user can complete their task.
    Task must be in Doing status.
    """
    use_case = container.complete_task_use_case()

    task = await use_case.execute(
        CompleteTaskInput(
            task_id=task_id,
            user_id=user_id,
        )
    )
    return TaskResponse.from_entity(task)


@router.post(
    "/{task_id}/abandon",
    response_model=TaskResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request or task status"},
        403: {"model": ErrorResponse, "description": "Not task owner"},
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def abandon_task(
    project_id: UUID,
    task_id: UUID,
    request: AbandonTaskRequest,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> TaskResponse:
    """
    Abandon a task that you are working on.

    BR-ABANDON-002: Reason is required.
    Task returns to Todo status and becomes unassigned.
    """
    use_case = container.abandon_task_use_case()

    task = await use_case.execute(
        AbandonTaskInput(
            task_id=task_id,
            user_id=user_id,
            reason=request.reason,
        )
    )
    return TaskResponse.from_entity(task)


@router.post(
    "/{task_id}/reports",
    response_model=TaskLogResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request or task status"},
        403: {"model": ErrorResponse, "description": "Not task owner"},
        404: {"model": ErrorResponse, "description": "Task not found"},
    },
)
async def add_task_report(
    project_id: UUID,
    task_id: UUID,
    request: AddReportRequest,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> TaskLogResponse:
    """
    Add a progress report to a task.

    UC-042: Only the assigned employee can add reports.
    Task must be in Doing status.
    """
    use_case = container.add_task_report_use_case()

    log = await use_case.execute(
        AddTaskReportInput(
            task_id=task_id,
            user_id=user_id,
            report_text=request.report_text,
        )
    )
    return TaskLogResponse.from_entity(log)


@router.post(
    "/{task_id}/remove-assignee",
    response_model=TaskResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Task not in Doing status"},
        403: {"model": ErrorResponse, "description": "Not authorized (not manager)"},
        404: {"model": ErrorResponse, "description": "Task not found"},
        422: {"model": ErrorResponse, "description": "Task not assigned"},
    },
)
async def remove_from_task(
    project_id: UUID,
    task_id: UUID,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> TaskResponse:
    """
    Forcibly remove an employee from a task (manager only).

    UC-050: Task returns to Todo status.
    """
    use_case = container.remove_from_task_use_case()

    task = await use_case.execute(
        RemoveFromTaskInput(
            task_id=task_id,
            manager_user_id=user_id,
        )
    )
    return TaskResponse.from_entity(task)


@router.post(
    "/{task_id}/cancel",
    response_model=TaskResponse,
    responses={
        403: {"model": ErrorResponse, "description": "Not authorized (not manager)"},
        404: {"model": ErrorResponse, "description": "Task or project not found"},
    },
)
async def cancel_task(
    project_id: UUID,
    task_id: UUID,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> TaskResponse:
    """Cancel a task (manager only)."""
    use_case = container.cancel_task_use_case()
    task = await use_case.execute(
        CancelTaskInput(
            project_id=project_id,
            task_id=task_id,
            manager_user_id=user_id,
        )
    )
    return TaskResponse.from_entity(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        403: {"model": ErrorResponse, "description": "Not authorized (not manager)"},
        404: {"model": ErrorResponse, "description": "Task or project not found"},
    },
)
async def delete_task(
    project_id: UUID,
    task_id: UUID,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> None:
    """Delete a task and related dependencies (manager only)."""
    use_case = container.delete_task_use_case()
    await use_case.execute(
        DeleteTaskInput(
            project_id=project_id,
            task_id=task_id,
            manager_user_id=user_id,
        )
    )


@router.post(
    "/{task_id}/dependencies",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid or circular dependency"},
        403: {"model": ErrorResponse, "description": "Not authorized (not manager)"},
        404: {"model": ErrorResponse, "description": "Task or project not found"},
    },
)
async def add_dependency(
    project_id: UUID,
    task_id: UUID,
    request: AddDependencyRequest,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> None:
    """Add dependency: task_id depends on blocking_task_id."""
    use_case = container.add_dependency_use_case()
    await use_case.execute(
        AddDependencyInput(
            project_id=project_id,
            blocking_task_id=request.blocking_task_id,
            blocked_task_id=task_id,
            manager_user_id=user_id,
        )
    )


@router.delete(
    "/{task_id}/dependencies/{blocking_task_id}",
    response_model=TaskResponse,
    responses={
        403: {"model": ErrorResponse, "description": "Not authorized (not manager)"},
        404: {"model": ErrorResponse, "description": "Task or dependency not found"},
    },
)
async def remove_dependency(
    project_id: UUID,
    task_id: UUID,
    blocking_task_id: UUID,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> TaskResponse:
    """Remove dependency: task_id no longer depends on blocking_task_id."""
    use_case = container.remove_dependency_use_case()
    task = await use_case.execute(
        RemoveDependencyInput(
            project_id=project_id,
            blocking_task_id=blocking_task_id,
            blocked_task_id=task_id,
            manager_user_id=user_id,
        )
    )
    return TaskResponse.from_entity(task)
