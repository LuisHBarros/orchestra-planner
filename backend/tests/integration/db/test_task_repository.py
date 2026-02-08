"""Integration tests for PostgresTaskRepository."""

from backend.src.adapters.db import PostgresProjectRepository, PostgresTaskRepository, PostgresUserRepository
from backend.src.domain.entities import Project, Task, User

import pytest


@pytest.mark.asyncio
async def test_task_repository_roundtrip(db_session):
    user_repo = PostgresUserRepository(db_session)
    project_repo = PostgresProjectRepository(db_session)
    repo = PostgresTaskRepository(db_session)

    manager = User(email="manager@example.com", name="Manager")
    await user_repo.save(manager)
    project = Project(name="Proj", manager_id=manager.id)
    await project_repo.save(project)

    task = Task(project_id=project.id, title="Task", difficulty_points=2)
    await repo.save(task)

    found = await repo.find_by_id(task.id)
    by_project = await repo.find_by_project(project.id)

    assert found is not None
    assert len(by_project) == 1
    assert by_project[0].id == task.id
