"""Tests for DeleteTaskUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.task_management.delete_task import (
    DeleteTaskInput,
    DeleteTaskUseCase,
)
from backend.src.domain.entities import Project, Task
from backend.src.domain.errors import ManagerRequiredError, ProjectNotFoundError, TaskNotFoundError


@pytest.fixture
def uow():
    mock = AsyncMock()
    mock.project_repository = AsyncMock()
    mock.task_repository = AsyncMock()
    mock.task_dependency_repository = AsyncMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=False)
    return mock


@pytest.fixture
def recalc_use_case():
    mock = AsyncMock()
    mock.execute = AsyncMock()
    return mock


@pytest.fixture
def use_case(uow, recalc_use_case):
    return DeleteTaskUseCase(uow=uow, recalculate_schedule_use_case=recalc_use_case)


@pytest.mark.asyncio
async def test_deletes_task_and_dependencies(use_case, uow, recalc_use_case):
    manager_id = uuid4()
    project = Project(name="P", manager_id=manager_id)
    task = Task(project_id=project.id, title="T", difficulty_points=1)

    uow.project_repository.find_by_id.return_value = project
    uow.task_repository.find_by_id.return_value = task

    await use_case.execute(
        DeleteTaskInput(
            project_id=project.id,
            task_id=task.id,
            manager_user_id=manager_id,
        )
    )

    uow.task_dependency_repository.delete.assert_awaited_once_with(task.id)
    uow.task_repository.delete.assert_awaited_once_with(task.id)
    uow.commit.assert_awaited_once()
    recalc_use_case.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_raises_on_missing_project_or_task(use_case, uow):
    uow.project_repository.find_by_id.return_value = None
    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(
            DeleteTaskInput(project_id=uuid4(), task_id=uuid4(), manager_user_id=uuid4())
        )

    manager_id = uuid4()
    project = Project(name="P", manager_id=manager_id)
    uow.project_repository.find_by_id.return_value = project
    uow.task_repository.find_by_id.return_value = None
    with pytest.raises(TaskNotFoundError):
        await use_case.execute(
            DeleteTaskInput(project_id=project.id, task_id=uuid4(), manager_user_id=manager_id)
        )


@pytest.mark.asyncio
async def test_raises_if_not_manager(use_case, uow):
    manager_id = uuid4()
    project = Project(name="P", manager_id=manager_id)
    task = Task(project_id=project.id, title="T", difficulty_points=1)

    uow.project_repository.find_by_id.return_value = project
    uow.task_repository.find_by_id.return_value = task

    with pytest.raises(ManagerRequiredError):
        await use_case.execute(
            DeleteTaskInput(project_id=project.id, task_id=task.id, manager_user_id=uuid4())
        )
