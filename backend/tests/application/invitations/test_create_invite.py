"""Tests for CreateInviteUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.invitations import (
    CreateInviteInput,
    CreateInviteUseCase,
)
from backend.src.domain.entities import Project, ProjectInvite, Role
from backend.src.domain.errors import ManagerRequiredError, ProjectNotFoundError


@pytest.fixture
def project_repository():
    return AsyncMock()


@pytest.fixture
def role_repository():
    return AsyncMock()


@pytest.fixture
def project_invite_repository():
    return AsyncMock()


@pytest.fixture
def use_case(project_repository, role_repository, project_invite_repository):
    return CreateInviteUseCase(
        project_repository=project_repository,
        role_repository=role_repository,
        project_invite_repository=project_invite_repository,
        base_url="http://test.example.com",
    )


@pytest.fixture
def manager_id():
    return uuid4()


@pytest.fixture
def existing_project(manager_id):
    return Project(name="Test Project", manager_id=manager_id)


@pytest.fixture
def existing_role(existing_project):
    return Role(project_id=existing_project.id, name="Developer")


class TestCreateInviteUseCase:
    """Tests for CreateInviteUseCase.execute()."""

    @pytest.mark.asyncio
    async def test_creates_invite_when_requester_is_manager(
        self,
        use_case,
        project_repository,
        role_repository,
        project_invite_repository,
        existing_project,
        existing_role,
        manager_id,
    ):
        """BR-INV-001: Only Managers can generate invite links."""
        project_repository.find_by_id.return_value = existing_project
        role_repository.find_by_id.return_value = existing_role
        project_invite_repository.save.return_value = None

        input_data = CreateInviteInput(
            project_id=existing_project.id,
            role_id=existing_role.id,
            requester_id=manager_id,
        )

        result = await use_case.execute(input_data)

        assert result.invite.project_id == existing_project.id
        assert result.invite.role_id == existing_role.id
        assert result.invite.created_by == manager_id
        assert result.invite.token is not None
        assert "http://test.example.com/invites/" in result.invite_url
        project_invite_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_invite_is_tied_to_project_and_role(
        self,
        use_case,
        project_repository,
        role_repository,
        project_invite_repository,
        existing_project,
        existing_role,
        manager_id,
    ):
        """BR-INV-002: An invite link is tied to a specific Project and Role."""
        project_repository.find_by_id.return_value = existing_project
        role_repository.find_by_id.return_value = existing_role
        project_invite_repository.save.return_value = None

        input_data = CreateInviteInput(
            project_id=existing_project.id,
            role_id=existing_role.id,
            requester_id=manager_id,
        )

        result = await use_case.execute(input_data)

        assert result.invite.project_id == existing_project.id
        assert result.invite.role_id == existing_role.id

    @pytest.mark.asyncio
    async def test_invite_token_is_generated(
        self,
        use_case,
        project_repository,
        role_repository,
        project_invite_repository,
        existing_project,
        existing_role,
        manager_id,
    ):
        """BR-INV-003: Invite links are public tokens."""
        project_repository.find_by_id.return_value = existing_project
        role_repository.find_by_id.return_value = existing_role
        project_invite_repository.save.return_value = None

        input_data = CreateInviteInput(
            project_id=existing_project.id,
            role_id=existing_role.id,
            requester_id=manager_id,
        )

        result = await use_case.execute(input_data)

        assert len(result.invite.token) > 0
        assert (
            result.invite_url
            == f"http://test.example.com/invites/{result.invite.token}"
        )

    @pytest.mark.asyncio
    async def test_raises_project_not_found(
        self,
        use_case,
        project_repository,
        role_repository,
        project_invite_repository,
    ):
        """Should raise ProjectNotFoundError when project doesn't exist."""
        project_repository.find_by_id.return_value = None

        input_data = CreateInviteInput(
            project_id=uuid4(),
            role_id=uuid4(),
            requester_id=uuid4(),
        )

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(input_data)

        project_invite_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_manager_required_when_not_manager(
        self,
        use_case,
        project_repository,
        role_repository,
        project_invite_repository,
        existing_project,
    ):
        """BR-INV-001: Only Managers can generate invite links."""
        project_repository.find_by_id.return_value = existing_project
        non_manager_id = uuid4()

        input_data = CreateInviteInput(
            project_id=existing_project.id,
            role_id=uuid4(),
            requester_id=non_manager_id,
        )

        with pytest.raises(ManagerRequiredError):
            await use_case.execute(input_data)

        project_invite_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_value_error_when_role_not_found(
        self,
        use_case,
        project_repository,
        role_repository,
        project_invite_repository,
        existing_project,
        manager_id,
    ):
        """Should raise ValueError when role doesn't exist."""
        project_repository.find_by_id.return_value = existing_project
        role_repository.find_by_id.return_value = None

        input_data = CreateInviteInput(
            project_id=existing_project.id,
            role_id=uuid4(),
            requester_id=manager_id,
        )

        with pytest.raises(ValueError, match="Role .* not found"):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_value_error_when_role_from_different_project(
        self,
        use_case,
        project_repository,
        role_repository,
        project_invite_repository,
        existing_project,
        manager_id,
    ):
        """Should raise ValueError when role belongs to different project."""
        different_project_role = Role(project_id=uuid4(), name="Other Role")
        project_repository.find_by_id.return_value = existing_project
        role_repository.find_by_id.return_value = different_project_role

        input_data = CreateInviteInput(
            project_id=existing_project.id,
            role_id=different_project_role.id,
            requester_id=manager_id,
        )

        with pytest.raises(ValueError, match="Role .* not found"):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_saves_invite_to_repository(
        self,
        use_case,
        project_repository,
        role_repository,
        project_invite_repository,
        existing_project,
        existing_role,
        manager_id,
    ):
        """Should save the invite using the repository."""
        project_repository.find_by_id.return_value = existing_project
        role_repository.find_by_id.return_value = existing_role
        project_invite_repository.save.return_value = None

        input_data = CreateInviteInput(
            project_id=existing_project.id,
            role_id=existing_role.id,
            requester_id=manager_id,
        )

        await use_case.execute(input_data)

        project_invite_repository.save.assert_called_once()
        saved_invite = project_invite_repository.save.call_args[0][0]
        assert isinstance(saved_invite, ProjectInvite)
