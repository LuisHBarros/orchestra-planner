"""Integration tests for PostgresProjectRepository."""

from backend.src.adapters.db import (
    PostgresProjectMemberRepository,
    PostgresProjectRepository,
    PostgresRoleRepository,
    PostgresUserRepository,
)
from backend.src.domain.entities import Project, ProjectMember, Role, SeniorityLevel, User

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


@pytest.mark.asyncio
async def test_project_repository_list_and_count_by_user_without_duplicates(db_session):
    user_repo = PostgresUserRepository(db_session)
    project_repo = PostgresProjectRepository(db_session)
    role_repo = PostgresRoleRepository(db_session)
    member_repo = PostgresProjectMemberRepository(db_session)

    manager = User(email="manager-list@example.com", name="Manager")
    member_user = User(email="member-list@example.com", name="Member")
    await user_repo.save(manager)
    await user_repo.save(member_user)

    owned = Project(name="Owned", manager_id=manager.id)
    shared = Project(name="Shared", manager_id=manager.id)
    outsider = Project(name="Outsider", manager_id=member_user.id)
    await project_repo.save(owned)
    await project_repo.save(shared)
    await project_repo.save(outsider)

    role = Role(project_id=shared.id, name="Dev")
    await role_repo.save(role)
    await member_repo.save(
        ProjectMember(
            project_id=shared.id,
            user_id=manager.id,
            role_id=role.id,
            seniority_level=SeniorityLevel.MID,
        )
    )

    listed = await project_repo.list_by_user(manager.id, limit=20, offset=0)
    counted = await project_repo.count_by_user(manager.id)

    listed_ids = {p.id for p in listed}
    assert owned.id in listed_ids
    assert shared.id in listed_ids
    assert outsider.id not in listed_ids
    assert counted == 2


@pytest.mark.asyncio
async def test_project_repository_list_by_user_pagination(db_session):
    user_repo = PostgresUserRepository(db_session)
    project_repo = PostgresProjectRepository(db_session)

    manager = User(email="manager-page@example.com", name="Manager")
    await user_repo.save(manager)
    for i in range(3):
        await project_repo.save(Project(name=f"Proj-{i}", manager_id=manager.id))

    page = await project_repo.list_by_user(manager.id, limit=2, offset=1)
    assert len(page) == 2
