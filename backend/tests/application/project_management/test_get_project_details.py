"""Tests for GetProjectDetailsUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.project_management import (
    GetProjectDetailsInput,
    GetProjectDetailsUseCase,
)
from backend.src.domain.entities import Project, ProjectMember, SeniorityLevel
from backend.src.domain.errors import ProjectAccessDeniedError, ProjectNotFoundError


@pytest.fixture
def project_repository():
    return AsyncMock()


@pytest.fixture
def project_member_repository():
    return AsyncMock()


@pytest.fixture
def use_case(project_repository, project_member_repository):
    return GetProjectDetailsUseCase(
        project_repository=project_repository,
        project_member_repository=project_member_repository,
    )


@pytest.fixture
def manager_id():
    return uuid4()


@pytest.fixture
def existing_project(manager_id):
    return Project(name="Test Project", manager_id=manager_id)


class TestGetProjectDetailsUseCase:
    """Tests for GetProjectDetailsUseCase.execute()."""

    @pytest.mark.asyncio
    async def test_returns_project_details_for_manager(
        self,
        use_case,
        project_repository,
        project_member_repository,
        existing_project,
        manager_id,
    ):
        """Manager can view project details."""
        project_repository.find_by_id.return_value = existing_project
        project_member_repository.find_by_project_and_user.return_value = None

        input_data = GetProjectDetailsInput(
            project_id=existing_project.id,
            requester_id=manager_id,
        )

        result = await use_case.execute(input_data)

        assert result.project == existing_project
        assert result.is_manager is True

    @pytest.mark.asyncio
    async def test_returns_project_details_for_member(
        self, use_case, project_repository, project_member_repository, existing_project
    ):
        """BR-PROJ-002: Only project members can view project details."""
        member_id = uuid4()
        role_id = uuid4()
        project_member = ProjectMember(
            project_id=existing_project.id,
            user_id=member_id,
            role_id=role_id,
            seniority_level=SeniorityLevel.MID,
        )
        project_repository.find_by_id.return_value = existing_project
        project_member_repository.find_by_project_and_user.return_value = project_member

        input_data = GetProjectDetailsInput(
            project_id=existing_project.id,
            requester_id=member_id,
        )

        result = await use_case.execute(input_data)

        assert result.project == existing_project
        assert result.is_manager is False

    @pytest.mark.asyncio
    async def test_raises_project_not_found_when_project_does_not_exist(
        self, use_case, project_repository, project_member_repository
    ):
        """Should raise ProjectNotFoundError when project doesn't exist."""
        project_repository.find_by_id.return_value = None
        project_id = uuid4()
        requester_id = uuid4()

        input_data = GetProjectDetailsInput(
            project_id=project_id,
            requester_id=requester_id,
        )

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_access_denied_when_requester_is_not_member(
        self, use_case, project_repository, project_member_repository, existing_project
    ):
        """BR-PROJ-002: Non-members cannot view project details."""
        non_member_id = uuid4()
        project_repository.find_by_id.return_value = existing_project
        project_member_repository.find_by_project_and_user.return_value = None

        input_data = GetProjectDetailsInput(
            project_id=existing_project.id,
            requester_id=non_member_id,
        )

        with pytest.raises(ProjectAccessDeniedError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_checks_membership_with_correct_parameters(
        self, use_case, project_repository, project_member_repository, existing_project
    ):
        """Should query membership with correct project and user IDs."""
        member_id = uuid4()
        role_id = uuid4()
        project_member = ProjectMember(
            project_id=existing_project.id,
            user_id=member_id,
            role_id=role_id,
            seniority_level=SeniorityLevel.SENIOR,
        )
        project_repository.find_by_id.return_value = existing_project
        project_member_repository.find_by_project_and_user.return_value = project_member

        input_data = GetProjectDetailsInput(
            project_id=existing_project.id,
            requester_id=member_id,
        )

        await use_case.execute(input_data)

        project_member_repository.find_by_project_and_user.assert_called_once_with(
            existing_project.id, member_id
        )
