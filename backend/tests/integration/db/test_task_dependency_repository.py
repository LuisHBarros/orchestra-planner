"""Integration tests for PostgresTaskDependencyRepository."""

from backend.src.adapters.db import (
    PostgresProjectRepository,
    PostgresTaskDependencyRepository,
    PostgresTaskRepository,
    PostgresUserRepository,
)
from backend.src.domain.entities import Project, Task, TaskDependency, User

import pytest


@pytest.mark.asyncio
async def test_task_dependency_repository_roundtrip(db_session):
    user_repo = PostgresUserRepository(db_session)
    project_repo = PostgresProjectRepository(db_session)
    task_repo = PostgresTaskRepository(db_session)
    repo = PostgresTaskDependencyRepository(db_session)

    manager = User(email="manager@example.com", name="Manager")
    await user_repo.save(manager)
    project = Project(name="Proj", manager_id=manager.id)
    await project_repo.save(project)

    parent = Task(project_id=project.id, title="A", difficulty_points=1)
    child = Task(project_id=project.id, title="B", difficulty_points=1)
    await task_repo.save(parent)
    await task_repo.save(child)

    dep = TaskDependency(blocking_task_id=parent.id, blocked_task_id=child.id)
    await repo.save(dep)

    found = await repo.find_by_tasks(parent.id, child.id)
    assert found is not None

    await repo.delete_by_tasks(parent.id, child.id)
    removed = await repo.find_by_tasks(parent.id, child.id)
    assert removed is None
