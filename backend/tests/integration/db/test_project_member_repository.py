"""Integration tests for PostgresProjectMemberRepository."""

from backend.src.adapters.db import (
    PostgresProjectMemberRepository,
    PostgresProjectRepository,
    PostgresRoleRepository,
    PostgresUserRepository,
)
from backend.src.domain.entities import Project, ProjectMember, Role, SeniorityLevel, User

import pytest


@pytest.mark.asyncio
async def test_project_member_repository_roundtrip(db_session):
    user_repo = PostgresUserRepository(db_session)
    project_repo = PostgresProjectRepository(db_session)
    role_repo = PostgresRoleRepository(db_session)
    repo = PostgresProjectMemberRepository(db_session)

    manager = User(email="manager@example.com", name="Manager")
    employee = User(email="employee@example.com", name="Emp")
    await user_repo.save(manager)
    await user_repo.save(employee)

    project = Project(name="Proj", manager_id=manager.id)
    await project_repo.save(project)

    role = Role(project_id=project.id, name="Dev")
    await role_repo.save(role)

    member = ProjectMember(
        project_id=project.id,
        user_id=employee.id,
        role_id=role.id,
        seniority_level=SeniorityLevel.MID,
    )
    await repo.save(member)

    found = await repo.find_by_project_and_user(project.id, employee.id)
    assert found is not None
    assert found.id == member.id
