"""Project management API endpoints."""

from datetime import date, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from backend.src.adapters.api.routers.common import get_container, get_current_user_id
from backend.src.application.use_cases.project_management import (
    ConfigureCalendarInput,
    ConfigureProjectLLMInput,
    CreateProjectInput,
    GetProjectDetailsInput,
)
from backend.src.domain.entities import Project
from backend.src.infrastructure.di import Container

router = APIRouter(prefix="/projects", tags=["projects"])


class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="", max_length=5000)


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str
    manager_id: UUID
    expected_end_date: datetime | None
    created_at: datetime

    @classmethod
    def from_entity(cls, project: Project) -> "ProjectResponse":
        return cls(
            id=project.id,
            name=project.name,
            description=project.description,
            manager_id=project.manager_id,
            expected_end_date=project.expected_end_date,
            created_at=project.created_at,
        )


class ProjectDetailsResponse(BaseModel):
    project: ProjectResponse
    is_manager: bool


class ConfigureProjectLLMRequest(BaseModel):
    provider: str = Field(..., min_length=1, max_length=100)
    api_key: str = Field(..., min_length=1)


class ConfigureCalendarRequest(BaseModel):
    timezone: str = Field(default="UTC", min_length=1, max_length=64)
    exclusion_dates: list[date] = Field(default_factory=list)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: CreateProjectRequest,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> ProjectResponse:
    use_case = container.create_project_use_case()
    project = await use_case.execute(
        CreateProjectInput(
            user_id=user_id,
            name=request.name,
            description=request.description,
        )
    )
    return ProjectResponse.from_entity(project)


@router.get("/{project_id}", response_model=ProjectDetailsResponse)
async def get_project_details(
    project_id: UUID,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> ProjectDetailsResponse:
    use_case = container.get_project_details_use_case()
    result = await use_case.execute(
        GetProjectDetailsInput(project_id=project_id, requester_id=user_id)
    )
    return ProjectDetailsResponse(
        project=ProjectResponse.from_entity(result.project),
        is_manager=result.is_manager,
    )


@router.post("/{project_id}/llm", status_code=status.HTTP_204_NO_CONTENT)
async def configure_project_llm(
    project_id: UUID,
    request: ConfigureProjectLLMRequest,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> None:
    use_case = container.configure_project_llm_use_case()
    await use_case.execute(
        ConfigureProjectLLMInput(
            project_id=project_id,
            requester_id=user_id,
            provider=request.provider,
            api_key=request.api_key,
        )
    )


@router.post("/{project_id}/calendar", status_code=status.HTTP_204_NO_CONTENT)
async def configure_calendar(
    project_id: UUID,
    request: ConfigureCalendarRequest,
    container: Annotated[Container, Depends(get_container)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> None:
    use_case = container.configure_calendar_use_case()
    await use_case.execute(
        ConfigureCalendarInput(
            project_id=project_id,
            requester_id=user_id,
            timezone=request.timezone,
            exclusion_dates=request.exclusion_dates,
        )
    )
