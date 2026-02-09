"""Integration tests for PostgresTaskLogRepository."""

from backend.src.adapters.db import (
    PostgresProjectMemberRepository,
    PostgresProjectRepository,
    PostgresRoleRepository,
    PostgresTaskLogRepository,
    PostgresTaskRepository,
    PostgresUserRepository,
)
from backend.src.domain.entities import (
    Project,
    ProjectMember,
    Role,
    SeniorityLevel,
    Task,
    TaskLog,
    User,
)

import pytest


@pytest.mark.asyncio
async def test_task_log_repository_roundtrip(db_session):
    user_repo = PostgresUserRepository(db_session)
    project_repo = PostgresProjectRepository(db_session)
    role_repo = PostgresRoleRepository(db_session)
    member_repo = PostgresProjectMemberRepository(db_session)
    task_repo = PostgresTaskRepository(db_session)
    repo = PostgresTaskLogRepository(db_session)

    manager = User(email="manager@example.com", name="Manager")
    employee = User(email="employee@example.com", name="Employee")
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
    await member_repo.save(member)

    task = Task(project_id=project.id, title="Task", difficulty_points=1)
    await task_repo.save(task)

    log = TaskLog.create_report_log(task_id=task.id, author_id=member.id, report_text="done")
    await repo.save(log)

    found = await repo.find_by_task(task.id)
    assert len(found) == 1
    assert found[0].content == "done"


@pytest.mark.asyncio
async def test_task_log_repository_pagination_and_count(db_session):
    user_repo = PostgresUserRepository(db_session)
    project_repo = PostgresProjectRepository(db_session)
    role_repo = PostgresRoleRepository(db_session)
    member_repo = PostgresProjectMemberRepository(db_session)
    task_repo = PostgresTaskRepository(db_session)
    repo = PostgresTaskLogRepository(db_session)

    manager = User(email="manager4@example.com", name="Manager")
    employee = User(email="employee4@example.com", name="Employee")
    await user_repo.save(manager)
    await user_repo.save(employee)

    project = Project(name="Proj4", manager_id=manager.id)
    await project_repo.save(project)
    role = Role(project_id=project.id, name="Dev")
    await role_repo.save(role)
    member = ProjectMember(
        project_id=project.id,
        user_id=employee.id,
        role_id=role.id,
        seniority_level=SeniorityLevel.MID,
    )
    await member_repo.save(member)
    task = Task(project_id=project.id, title="Task2", difficulty_points=1)
    await task_repo.save(task)

    for i in range(3):
        log = TaskLog.create_report_log(
            task_id=task.id,
            author_id=member.id,
            report_text=f"r{i}",
        )
        await repo.save(log)

    assert await repo.count_by_task(task.id) == 3
    page = await repo.list_by_task(task.id, limit=2, offset=1)
    assert len(page) == 2
