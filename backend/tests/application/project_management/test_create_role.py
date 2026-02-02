"""Tests for CreateRoleUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.project_management import (
    CreateRoleInput,
    CreateRoleUseCase,
)
from backend.src.domain.entities import Project, Role
from backend.src.domain.errors import ManagerRequiredError, ProjectNotFoundError


@pytest.fixture
def project_repository():
    return AsyncMock()


@pytest.fixture
def role_repository():
    return AsyncMock()


@pytest.fixture
def use_case(project_repository, role_repository):
    return CreateRoleUseCase(
        project_repository=project_repository,
        role_repository=role_repository,
    )


@pytest.fixture
def manager_id():
    return uuid4()


@pytest.fixture
def existing_project(manager_id):
    return Project(name="Test Project", manager_id=manager_id)


class TestCreateRoleUseCase:
    """Tests for CreateRoleUseCase.execute()."""

    @pytest.mark.asyncio
    async def test_creates_role_when_requester_is_manager(
        self,
        use_case,
        project_repository,
        role_repository,
        existing_project,
        manager_id,
    ):
        """BR-ROLE-001: Roles are created by the Manager."""
        project_repository.find_by_id.return_value = existing_project
        role_repository.save.return_value = None

        input_data = CreateRoleInput(
            project_id=existing_project.id,
            requester_id=manager_id,
            role_name="Backend Developer",
        )

        result = await use_case.execute(input_data)

        assert result.name == "Backend Developer"
        assert result.project_id == existing_project.id
        role_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_project_not_found_when_project_does_not_exist(
        self, use_case, project_repository, role_repository
    ):
        """Should raise ProjectNotFoundError when project doesn't exist."""
        project_repository.find_by_id.return_value = None
        project_id = uuid4()
        requester_id = uuid4()

        input_data = CreateRoleInput(
            project_id=project_id,
            requester_id=requester_id,
            role_name="Backend Developer",
        )

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(input_data)

        role_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_manager_required_when_requester_is_not_manager(
        self, use_case, project_repository, role_repository, existing_project
    ):
        """BR-PROJ-004: Only the Manager can edit Project settings."""
        project_repository.find_by_id.return_value = existing_project
        non_manager_id = uuid4()

        input_data = CreateRoleInput(
            project_id=existing_project.id,
            requester_id=non_manager_id,
            role_name="Backend Developer",
        )

        with pytest.raises(ManagerRequiredError):
            await use_case.execute(input_data)

        role_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_saves_role_to_repository(
        self,
        use_case,
        project_repository,
        role_repository,
        existing_project,
        manager_id,
    ):
        """Should save the role using the repository."""
        project_repository.find_by_id.return_value = existing_project
        role_repository.save.return_value = None

        input_data = CreateRoleInput(
            project_id=existing_project.id,
            requester_id=manager_id,
            role_name="Frontend Developer",
        )

        await use_case.execute(input_data)

        role_repository.save.assert_called_once()
        saved_role = role_repository.save.call_args[0][0]
        assert isinstance(saved_role, Role)
        assert saved_role.name == "Frontend Developer"
        assert saved_role.project_id == existing_project.id
