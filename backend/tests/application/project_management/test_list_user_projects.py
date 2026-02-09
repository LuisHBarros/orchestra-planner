"""Tests for ListUserProjectsUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.project_management import (
    ListUserProjectsInput,
    ListUserProjectsUseCase,
)
from backend.src.domain.entities import Project


@pytest.fixture
def uow():
    mock = AsyncMock()
    mock.project_repository = AsyncMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=False)
    return mock


@pytest.fixture
def use_case(uow):
    return ListUserProjectsUseCase(uow=uow)


class TestListUserProjectsUseCase:
    """Tests for ListUserProjectsUseCase.execute()."""

    @pytest.mark.asyncio
    async def test_returns_projects_and_total(self, use_case, uow):
        """Happy path: returns correct items and total."""
        user_id = uuid4()
        projects = [
            Project(name="Project A", manager_id=user_id),
            Project(name="Project B", manager_id=user_id),
        ]
        uow.project_repository.list_by_user.return_value = projects
        uow.project_repository.count_by_user.return_value = 2

        result = await use_case.execute(
            ListUserProjectsInput(user_id=user_id, limit=20, offset=0)
        )

        assert result.items == projects
        assert result.total == 2

    @pytest.mark.asyncio
    async def test_passes_pagination_to_repo(self, use_case, uow):
        """Pagination: passes limit/offset to repo correctly."""
        user_id = uuid4()
        uow.project_repository.list_by_user.return_value = []
        uow.project_repository.count_by_user.return_value = 0

        await use_case.execute(
            ListUserProjectsInput(user_id=user_id, limit=10, offset=5)
        )

        uow.project_repository.list_by_user.assert_called_once_with(
            user_id, limit=10, offset=5
        )
        uow.project_repository.count_by_user.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_projects(self, use_case, uow):
        """Returns empty list when user has no projects."""
        user_id = uuid4()
        uow.project_repository.list_by_user.return_value = []
        uow.project_repository.count_by_user.return_value = 0

        result = await use_case.execute(
            ListUserProjectsInput(user_id=user_id, limit=20, offset=0)
        )

        assert result.items == []
        assert result.total == 0
