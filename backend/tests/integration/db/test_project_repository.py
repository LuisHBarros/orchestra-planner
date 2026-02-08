"""Integration tests for PostgresProjectRepository."""

from backend.src.adapters.db import PostgresProjectRepository, PostgresUserRepository
from backend.src.domain.entities import Project, User

import pytest


@pytest.mark.asyncio
async def test_project_repository_roundtrip(db_session):
    user_repo = PostgresUserRepository(db_session)
    repo = PostgresProjectRepository(db_session)

    manager = User(email="manager@example.com", name="Manager")
    await user_repo.save(manager)

    project = Project(name="Proj", manager_id=manager.id)
    await repo.save(project)

    found = await repo.find_by_id(project.id)
    assert found is not None
    assert found.name == "Proj"
    assert found.manager_id == manager.id
