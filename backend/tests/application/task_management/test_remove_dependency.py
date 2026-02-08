"""Tests for RemoveDependencyUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.task_management.remove_dependency import (
    RemoveDependencyInput,
    RemoveDependencyUseCase,
)
from backend.src.domain.entities import Project, Task, TaskDependency, TaskStatus
from backend.src.domain.errors import ManagerRequiredError


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
    return RemoveDependencyUseCase(
        uow=uow,
        recalculate_schedule_use_case=recalc_use_case,
    )


@pytest.mark.asyncio
async def test_removes_dependency_and_unblocks_task(use_case, uow, recalc_use_case):
    manager_id = uuid4()
    project = Project(name="P", manager_id=manager_id)
    blocking = Task(project_id=project.id, title="A", difficulty_points=1)
    blocked = Task(project_id=project.id, title="B", difficulty_points=1)
    blocked.block()

    dep = TaskDependency(blocking_task_id=blocking.id, blocked_task_id=blocked.id)

    uow.project_repository.find_by_id.return_value = project
    uow.task_repository.find_by_id.return_value = blocked
    uow.task_dependency_repository.find_by_tasks.return_value = dep
    uow.task_dependency_repository.find_by_project.return_value = []

    task = await use_case.execute(
        RemoveDependencyInput(
            project_id=project.id,
            blocking_task_id=blocking.id,
            blocked_task_id=blocked.id,
            manager_user_id=manager_id,
        )
    )

    assert task.status == TaskStatus.TODO
    uow.task_dependency_repository.delete_by_tasks.assert_awaited_once_with(
        blocking.id,
        blocked.id,
    )
    uow.task_repository.save.assert_awaited_once_with(blocked)
    recalc_use_case.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_keeps_blocked_if_other_open_blockers(use_case, uow):
    manager_id = uuid4()
    project = Project(name="P", manager_id=manager_id)
    b1 = Task(project_id=project.id, title="A", difficulty_points=1)
    b2 = Task(project_id=project.id, title="C", difficulty_points=1)
    blocked = Task(project_id=project.id, title="B", difficulty_points=1)
    blocked.block()

    dep = TaskDependency(blocking_task_id=b1.id, blocked_task_id=blocked.id)
    remaining = TaskDependency(blocking_task_id=b2.id, blocked_task_id=blocked.id)

    uow.project_repository.find_by_id.return_value = project
    uow.task_repository.find_by_id.return_value = blocked
    uow.task_dependency_repository.find_by_tasks.return_value = dep
    uow.task_dependency_repository.find_by_project.return_value = [remaining]
    uow.task_repository.find_by_project.return_value = [b2, blocked]

    task = await use_case.execute(
        RemoveDependencyInput(
            project_id=project.id,
            blocking_task_id=b1.id,
            blocked_task_id=blocked.id,
            manager_user_id=manager_id,
        )
    )

    assert task.status == TaskStatus.BLOCKED
    uow.task_repository.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_raises_if_not_manager(use_case, uow):
    manager_id = uuid4()
    project = Project(name="P", manager_id=manager_id)
    blocked = Task(project_id=project.id, title="B", difficulty_points=1)

    uow.project_repository.find_by_id.return_value = project
    uow.task_repository.find_by_id.return_value = blocked

    with pytest.raises(ManagerRequiredError):
        await use_case.execute(
            RemoveDependencyInput(
                project_id=project.id,
                blocking_task_id=uuid4(),
                blocked_task_id=blocked.id,
                manager_user_id=uuid4(),
            )
        )
