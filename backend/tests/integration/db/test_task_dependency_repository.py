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


@pytest.mark.asyncio
async def test_task_dependency_repository_pagination_and_count(db_session):
    user_repo = PostgresUserRepository(db_session)
    project_repo = PostgresProjectRepository(db_session)
    task_repo = PostgresTaskRepository(db_session)
    repo = PostgresTaskDependencyRepository(db_session)

    manager = User(email="manager5@example.com", name="Manager")
    await user_repo.save(manager)
    project = Project(name="Proj5", manager_id=manager.id)
    await project_repo.save(project)

    tasks = []
    for label in ("A", "B", "C", "D"):
        task = Task(project_id=project.id, title=label, difficulty_points=1)
        await task_repo.save(task)
        tasks.append(task)

    await repo.save(
        TaskDependency(blocking_task_id=tasks[0].id, blocked_task_id=tasks[1].id)
    )
    await repo.save(
        TaskDependency(blocking_task_id=tasks[1].id, blocked_task_id=tasks[2].id)
    )
    await repo.save(
        TaskDependency(blocking_task_id=tasks[2].id, blocked_task_id=tasks[3].id)
    )

    assert await repo.count_by_project(project.id) == 3
    page = await repo.list_by_project(project.id, limit=2, offset=1)
    assert len(page) == 2
