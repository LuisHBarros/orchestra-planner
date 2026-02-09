"""Tests for ListProjectMembersUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.project_management import (
    ListProjectMembersInput,
    ListProjectMembersUseCase,
)
from backend.src.domain.entities import Project, ProjectMember, Role, SeniorityLevel, User
from backend.src.domain.errors import ProjectAccessDeniedError, ProjectNotFoundError


@pytest.fixture
def uow():
    mock = AsyncMock()
    mock.project_repository = AsyncMock()
    mock.project_member_repository = AsyncMock()
    mock.user_repository = AsyncMock()
    mock.role_repository = AsyncMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=False)
    return mock


@pytest.fixture
def use_case(uow):
    return ListProjectMembersUseCase(uow=uow)


@pytest.fixture
def manager_id():
    return uuid4()


@pytest.fixture
def project(manager_id):
    return Project(name="Test Project", manager_id=manager_id)


class TestListProjectMembersUseCase:
    """Tests for ListProjectMembersUseCase.execute()."""

    @pytest.mark.asyncio
    async def test_returns_enriched_members_for_manager(
        self, use_case, uow, project, manager_id
    ):
        """Happy path: manager can list members with enriched info."""
        role = Role(project_id=project.id, name="Developer")
        user = User(email="alice@test.com", name="Alice")
        member = ProjectMember(
            project_id=project.id,
            user_id=user.id,
            role_id=role.id,
            seniority_level=SeniorityLevel.MID,
        )

        uow.project_repository.find_by_id.return_value = project
        uow.project_member_repository.list_by_project.return_value = [member]
        uow.project_member_repository.count_by_project.return_value = 1
        uow.user_repository.find_by_id.return_value = user
        uow.role_repository.find_by_id.return_value = role

        result = await use_case.execute(
            ListProjectMembersInput(
                project_id=project.id,
                requester_id=manager_id,
                limit=50,
                offset=0,
            )
        )

        assert len(result.items) == 1
        assert result.total == 1
        assert result.items[0].user_name == "Alice"
        assert result.items[0].user_email == "alice@test.com"
        assert result.items[0].role_name == "Developer"
        assert result.items[0].seniority_level == "Mid"

    @pytest.mark.asyncio
    async def test_returns_enriched_members_for_member(
        self, use_case, uow, project
    ):
        """A project member can also list members."""
        member_user_id = uuid4()
        role = Role(project_id=project.id, name="Designer")
        user = User(email="bob@test.com", name="Bob")
        member = ProjectMember(
            project_id=project.id,
            user_id=user.id,
            role_id=role.id,
            seniority_level=SeniorityLevel.SENIOR,
        )
        requester_member = ProjectMember(
            project_id=project.id,
            user_id=member_user_id,
            role_id=role.id,
            seniority_level=SeniorityLevel.MID,
        )

        uow.project_repository.find_by_id.return_value = project
        uow.project_member_repository.find_by_project_and_user.return_value = requester_member
        uow.project_member_repository.list_by_project.return_value = [member]
        uow.project_member_repository.count_by_project.return_value = 1
        uow.user_repository.find_by_id.return_value = user
        uow.role_repository.find_by_id.return_value = role

        result = await use_case.execute(
            ListProjectMembersInput(
                project_id=project.id,
                requester_id=member_user_id,
                limit=50,
                offset=0,
            )
        )

        assert len(result.items) == 1
        assert result.items[0].user_name == "Bob"

    @pytest.mark.asyncio
    async def test_raises_project_not_found(self, use_case, uow):
        """Should raise ProjectNotFoundError when project doesn't exist."""
        uow.project_repository.find_by_id.return_value = None

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                ListProjectMembersInput(
                    project_id=uuid4(),
                    requester_id=uuid4(),
                    limit=50,
                    offset=0,
                )
            )

    @pytest.mark.asyncio
    async def test_raises_access_denied_for_non_member(
        self, use_case, uow, project
    ):
        """Should raise ProjectAccessDeniedError for non-member."""
        non_member_id = uuid4()
        uow.project_repository.find_by_id.return_value = project
        uow.project_member_repository.find_by_project_and_user.return_value = None

        with pytest.raises(ProjectAccessDeniedError):
            await use_case.execute(
                ListProjectMembersInput(
                    project_id=project.id,
                    requester_id=non_member_id,
                    limit=50,
                    offset=0,
                )
            )

    @pytest.mark.asyncio
    async def test_passes_pagination_to_repo(
        self, use_case, uow, project, manager_id
    ):
        """Pagination: passes limit/offset to repo correctly."""
        uow.project_repository.find_by_id.return_value = project
        uow.project_member_repository.list_by_project.return_value = []
        uow.project_member_repository.count_by_project.return_value = 0

        await use_case.execute(
            ListProjectMembersInput(
                project_id=project.id,
                requester_id=manager_id,
                limit=10,
                offset=5,
            )
        )

        uow.project_member_repository.list_by_project.assert_called_once_with(
            project.id, limit=10, offset=5
        )
