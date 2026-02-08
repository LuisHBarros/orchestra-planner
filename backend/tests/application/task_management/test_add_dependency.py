"""Tests for AddDependencyUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.task_management.add_dependency import (
    AddDependencyInput,
    AddDependencyUseCase,
)
from backend.src.domain.entities import Project, Task, TaskDependency, TaskStatus
from backend.src.domain.errors import CircularDependencyError, ManagerRequiredError


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
    return AddDependencyUseCase(uow=uow, recalculate_schedule_use_case=recalc_use_case)


@pytest.mark.asyncio
async def test_adds_dependency_and_blocks_child(use_case, uow, recalc_use_case):
    manager_id = uuid4()
    project = Project(name="P", manager_id=manager_id)
    blocking = Task(project_id=project.id, title="A", difficulty_points=1)
    blocked = Task(project_id=project.id, title="B", difficulty_points=1)

    uow.project_repository.find_by_id.return_value = project
    uow.task_repository.find_by_id.side_effect = [blocking, blocked]
    uow.task_dependency_repository.find_by_project.return_value = []
    uow.task_dependency_repository.find_by_tasks.return_value = None

    dep = await use_case.execute(
        AddDependencyInput(
            project_id=project.id,
            blocking_task_id=blocking.id,
            blocked_task_id=blocked.id,
            manager_user_id=manager_id,
        )
    )

    assert isinstance(dep, TaskDependency)
    assert blocked.status == TaskStatus.BLOCKED
    uow.task_dependency_repository.save.assert_awaited_once()
    uow.task_repository.save.assert_awaited_once_with(blocked)
    recalc_use_case.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_raises_for_cycle(use_case, uow):
    manager_id = uuid4()
    project = Project(name="P", manager_id=manager_id)
    a = Task(project_id=project.id, title="A", difficulty_points=1)
    b = Task(project_id=project.id, title="B", difficulty_points=1)

    uow.project_repository.find_by_id.return_value = project
    uow.task_repository.find_by_id.side_effect = [a, b]
    uow.task_dependency_repository.find_by_project.return_value = [
        TaskDependency(blocking_task_id=b.id, blocked_task_id=a.id)
    ]

    with pytest.raises(CircularDependencyError):
        await use_case.execute(
            AddDependencyInput(
                project_id=project.id,
                blocking_task_id=a.id,
                blocked_task_id=b.id,
                manager_user_id=manager_id,
            )
        )


@pytest.mark.asyncio
async def test_raises_if_not_manager(use_case, uow):
    manager_id = uuid4()
    project = Project(name="P", manager_id=manager_id)
    a = Task(project_id=project.id, title="A", difficulty_points=1)
    b = Task(project_id=project.id, title="B", difficulty_points=1)

    uow.project_repository.find_by_id.return_value = project
    uow.task_repository.find_by_id.side_effect = [a, b]

    with pytest.raises(ManagerRequiredError):
        await use_case.execute(
            AddDependencyInput(
                project_id=project.id,
                blocking_task_id=a.id,
                blocked_task_id=b.id,
                manager_user_id=uuid4(),
            )
        )
