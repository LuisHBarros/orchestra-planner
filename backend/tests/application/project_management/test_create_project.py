"""Tests for CreateProjectUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.project_management import (
    CreateProjectInput,
    CreateProjectUseCase,
)
from backend.src.domain.entities import Project, User
from backend.src.domain.errors import UserNotFoundError


@pytest.fixture
def user_repository():
    return AsyncMock()


@pytest.fixture
def project_repository():
    return AsyncMock()


@pytest.fixture
def use_case(user_repository, project_repository):
    return CreateProjectUseCase(
        user_repository=user_repository,
        project_repository=project_repository,
    )


@pytest.fixture
def existing_user():
    return User(email="manager@example.com", name="Manager")


class TestCreateProjectUseCase:
    """Tests for CreateProjectUseCase.execute()."""

    @pytest.mark.asyncio
    async def test_creates_project_with_user_as_manager(
        self, use_case, user_repository, project_repository, existing_user
    ):
        """BR-PROJ-001: The User who creates a Project is automatically assigned as the Manager."""
        user_repository.find_by_id.return_value = existing_user
        project_repository.save.return_value = None

        input_data = CreateProjectInput(
            user_id=existing_user.id,
            name="Test Project",
            description="A test project",
        )

        result = await use_case.execute(input_data)

        assert result.name == "Test Project"
        assert result.description == "A test project"
        assert result.manager_id == existing_user.id
        project_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_creates_project_without_description(
        self, use_case, user_repository, project_repository, existing_user
    ):
        """Project can be created with empty description."""
        user_repository.find_by_id.return_value = existing_user
        project_repository.save.return_value = None

        input_data = CreateProjectInput(
            user_id=existing_user.id,
            name="Test Project",
        )

        result = await use_case.execute(input_data)

        assert result.name == "Test Project"
        assert result.description == ""
        assert result.manager_id == existing_user.id

    @pytest.mark.asyncio
    async def test_raises_user_not_found_when_user_does_not_exist(
        self, use_case, user_repository, project_repository
    ):
        """Should raise UserNotFoundError when user doesn't exist."""
        user_repository.find_by_id.return_value = None
        user_id = uuid4()

        input_data = CreateProjectInput(
            user_id=user_id,
            name="Test Project",
            description="A test project",
        )

        with pytest.raises(UserNotFoundError):
            await use_case.execute(input_data)

        project_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_saves_project_to_repository(
        self, use_case, user_repository, project_repository, existing_user
    ):
        """Should save the project using the repository."""
        user_repository.find_by_id.return_value = existing_user
        project_repository.save.return_value = None

        input_data = CreateProjectInput(
            user_id=existing_user.id,
            name="Test Project",
            description="A test project",
        )

        await use_case.execute(input_data)

        project_repository.save.assert_called_once()
        saved_project = project_repository.save.call_args[0][0]
        assert isinstance(saved_project, Project)
        assert saved_project.name == "Test Project"
        assert saved_project.manager_id == existing_user.id
