"""Integration tests for PostgresCalendarRepository."""

from datetime import date

from backend.src.adapters.db import PostgresCalendarRepository, PostgresProjectRepository, PostgresUserRepository
from backend.src.domain.entities import Calendar, ExclusionDate, Project, User

import pytest


@pytest.mark.asyncio
async def test_calendar_repository_roundtrip(db_session):
    user_repo = PostgresUserRepository(db_session)
    project_repo = PostgresProjectRepository(db_session)
    repo = PostgresCalendarRepository(db_session)

    manager = User(email="manager@example.com", name="Manager")
    await user_repo.save(manager)
    project = Project(name="Proj", manager_id=manager.id)
    await project_repo.save(project)

    calendar = Calendar(
        project_id=project.id,
        timezone="UTC",
        exclusion_dates=frozenset({ExclusionDate(day=date(2026, 1, 1))}),
    )
    await repo.save(calendar)

    found = await repo.get_by_project_id(project.id)
    assert found is not None
    assert found.timezone == "UTC"
    assert len(found.exclusion_dates) == 1
