"""Tests for ConfigureCalendarUseCase."""

from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.project_management.configure_calendar import (
    ConfigureCalendarInput,
    ConfigureCalendarUseCase,
)
from backend.src.domain.entities import Calendar, Project
from backend.src.domain.errors import ManagerRequiredError, ProjectNotFoundError


@pytest.fixture
def project_repository():
    return AsyncMock()


@pytest.fixture
def calendar_repository():
    return AsyncMock()


@pytest.fixture
def recalc_use_case():
    mock = AsyncMock()
    mock.execute = AsyncMock()
    return mock


@pytest.fixture
def use_case(project_repository, calendar_repository, recalc_use_case):
    return ConfigureCalendarUseCase(
        project_repository=project_repository,
        calendar_repository=calendar_repository,
        recalculate_schedule_use_case=recalc_use_case,
    )


@pytest.mark.asyncio
async def test_updates_existing_calendar(use_case, project_repository, calendar_repository, recalc_use_case):
    manager_id = uuid4()
    project = Project(name="P", manager_id=manager_id)
    calendar = Calendar(project_id=project.id)

    project_repository.find_by_id.return_value = project
    calendar_repository.get_by_project_id.return_value = calendar
    calendar_repository.save.return_value = calendar

    result = await use_case.execute(
        ConfigureCalendarInput(
            project_id=project.id,
            requester_id=manager_id,
            timezone="UTC",
            exclusion_dates=[date(2026, 1, 1)],
        )
    )

    assert result.timezone == "UTC"
    assert len(result.exclusion_dates) == 1
    calendar_repository.save.assert_awaited_once()
    recalc_use_case.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_creates_calendar_if_missing(use_case, project_repository, calendar_repository):
    manager_id = uuid4()
    project = Project(name="P", manager_id=manager_id)

    project_repository.find_by_id.return_value = project
    calendar_repository.get_by_project_id.return_value = None
    calendar_repository.save.side_effect = lambda c: c

    result = await use_case.execute(
        ConfigureCalendarInput(project_id=project.id, requester_id=manager_id)
    )

    assert result.project_id == project.id
    calendar_repository.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_raises_for_missing_project_or_permissions(use_case, project_repository):
    project_repository.find_by_id.return_value = None
    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(
            ConfigureCalendarInput(project_id=uuid4(), requester_id=uuid4())
        )

    manager_id = uuid4()
    project = Project(name="P", manager_id=manager_id)
    project_repository.find_by_id.return_value = project
    with pytest.raises(ManagerRequiredError):
        await use_case.execute(
            ConfigureCalendarInput(project_id=project.id, requester_id=uuid4())
        )
