"""Integration tests for PostgresRoleRepository."""

from backend.src.adapters.db import PostgresProjectRepository, PostgresRoleRepository, PostgresUserRepository
from backend.src.domain.entities import Project, Role, User

import pytest


@pytest.mark.asyncio
async def test_role_repository_roundtrip(db_session):
    user_repo = PostgresUserRepository(db_session)
    project_repo = PostgresProjectRepository(db_session)
    repo = PostgresRoleRepository(db_session)

    manager = User(email="manager@example.com", name="Manager")
    await user_repo.save(manager)
    project = Project(name="Proj", manager_id=manager.id)
    await project_repo.save(project)

    role = Role(project_id=project.id, name="Developer")
    await repo.save(role)

    found = await repo.find_by_id(role.id)
    assert found is not None
    assert found.name == "Developer"
