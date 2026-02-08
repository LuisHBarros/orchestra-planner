"""Integration tests for PostgresProjectInviteRepository."""

from backend.src.adapters.db import (
    PostgresProjectInviteRepository,
    PostgresProjectRepository,
    PostgresRoleRepository,
    PostgresUserRepository,
)
from backend.src.domain.entities import Project, ProjectInvite, Role, User

import pytest


@pytest.mark.asyncio
async def test_project_invite_repository_roundtrip(db_session):
    user_repo = PostgresUserRepository(db_session)
    project_repo = PostgresProjectRepository(db_session)
    role_repo = PostgresRoleRepository(db_session)
    repo = PostgresProjectInviteRepository(db_session)

    manager = User(email="manager@example.com", name="Manager")
    await user_repo.save(manager)

    project = Project(name="Proj", manager_id=manager.id)
    await project_repo.save(project)

    role = Role(project_id=project.id, name="Dev")
    await role_repo.save(role)

    invite = ProjectInvite(project_id=project.id, role_id=role.id, created_by=manager.id)
    await repo.save(invite)

    found = await repo.find_by_token(invite.token)
    assert found is not None
    assert found.project_id == project.id
