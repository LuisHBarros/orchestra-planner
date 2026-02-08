"""Task management API endpoints."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.application.use_cases.task_management import (
    AbandonTaskInput,
    AddTaskReportInput,
    CompleteTaskInput,
    CreateTaskInput,
    RemoveFromTaskInput,
    SelectTaskInput,
)
from backend.src.domain.entities import Task, TaskLog, TaskStatus
from backend.src.infrastructure.db.session import get_db
from backend.src.infrastructure.di import Container, ContainerFactory

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


# --- Dependencies ---

# This would typically be initialized at app startup with real service implementations
_container_factory: ContainerFactory | None = None

# Injectable user ID provider for authentication
# Override this dependency in tests or when wiring real auth middleware
_current_user_id_provider: "CurrentUserIdProvider | None" = None


class CurrentUserIdProvider:
    """
    Protocol for providing the current authenticated user ID.

    Implement this interface and set it via set_current_user_provider()
    to integrate with your authentication system.
    """

    async def get_user_id(self) -> UUID:
        """Return the authenticated user's ID."""
        raise NotImplementedError


def get_container_factory() -> ContainerFactory:
    """Get the container factory (initialized at app startup)."""
    if _container_factory is None:
        raise RuntimeError("ContainerFactory not initialized")
    return _container_factory


def set_container_factory(factory: ContainerFactory) -> None:
    """Set the container factory (called at app startup)."""
    global _container_factory
    _container_factory = factory


def set_current_user_provider(provider: CurrentUserIdProvider) -> None:
    """Set the current user ID provider (called at app startup)."""
    global _current_user_id_provider
    _current_user_id_provider = provider


async def get_container(
    session: Annotated[AsyncSession, Depends(get_db)],
    factory: Annotated[ContainerFactory, Depends(get_container_factory)],
) -> Container:
    """FastAPI dependency for obtaining a DI container."""
    return factory.create(session)


async def get_current_user_id() -> UUID:
    """
    Get the current authenticated user's ID.

    This dependency requires a CurrentUserIdProvider to be configured
    via set_current_user_provider() at application startup.

    In tests, use FastAPI's dependency_overrides to provide a mock user ID.
    """
    if _current_user_id_provider is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication not configured",
        )
    return await _current_user_id_provider.get_user_id()


# --- Helpers ---


async def validate_task_belongs_to_project(
    container: Container,
    task_id: UUID,
    project_id: UUID,
) -> Task:
    """
    Validate that a task exists and belongs to the specified project.

    Returns the task if valid, raises HTTPException otherwise.
    """
    task = await container.repositories.task.find_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    if task.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found in project {project_id}",
        )
    return task


# --- Endpoints ---


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
    # Validate task belongs to project
    await validate_task_belongs_to_project(container, task_id, project_id)

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
    # Validate task belongs to project
    await validate_task_belongs_to_project(container, task_id, project_id)

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
    # Validate task belongs to project
    await validate_task_belongs_to_project(container, task_id, project_id)

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
    # Validate task belongs to project
    await validate_task_belongs_to_project(container, task_id, project_id)

    use_case = container.remove_from_task_use_case()

    task = await use_case.execute(
        RemoveFromTaskInput(
            task_id=task_id,
            manager_user_id=user_id,
        )
    )
    return TaskResponse.from_entity(task)
