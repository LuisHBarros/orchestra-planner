"""Tests for CreateTaskUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.task_management import (
    CreateTaskInput,
    CreateTaskUseCase,
)
from backend.src.domain.entities import Project, Task
from backend.src.domain.errors import ManagerRequiredError, ProjectNotFoundError


@pytest.fixture
def project_repository():
    return AsyncMock()


@pytest.fixture
def task_repository():
    return AsyncMock()


@pytest.fixture
def use_case(project_repository, task_repository):
    return CreateTaskUseCase(
        project_repository=project_repository,
        task_repository=task_repository,
    )


@pytest.fixture
def manager_id():
    return uuid4()


@pytest.fixture
def existing_project(manager_id):
    return Project(name="Test Project", manager_id=manager_id)


class TestCreateTaskUseCase:
    """Tests for CreateTaskUseCase.execute()."""

    @pytest.mark.asyncio
    async def test_creates_task_when_requester_is_manager(
        self,
        use_case,
        project_repository,
        task_repository,
        existing_project,
        manager_id,
    ):
        """BR-TASK-001: Only the Manager can create Tasks."""
        project_repository.find_by_id.return_value = existing_project
        task_repository.save.return_value = None

        input_data = CreateTaskInput(
            project_id=existing_project.id,
            requester_id=manager_id,
            title="Implement login",
            description="Add user authentication",
            difficulty_points=5,
        )

        result = await use_case.execute(input_data)

        assert result.title == "Implement login"
        assert result.description == "Add user authentication"
        assert result.difficulty_points == 5
        assert result.project_id == existing_project.id
        task_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_creates_task_without_difficulty(
        self,
        use_case,
        project_repository,
        task_repository,
        existing_project,
        manager_id,
    ):
        """Task can be created without difficulty points."""
        project_repository.find_by_id.return_value = existing_project
        task_repository.save.return_value = None

        input_data = CreateTaskInput(
            project_id=existing_project.id,
            requester_id=manager_id,
            title="Research task",
        )

        result = await use_case.execute(input_data)

        assert result.title == "Research task"
        assert result.difficulty_points is None

    @pytest.mark.asyncio
    async def test_creates_task_with_required_role(
        self,
        use_case,
        project_repository,
        task_repository,
        existing_project,
        manager_id,
    ):
        """Task can be created with a required role."""
        project_repository.find_by_id.return_value = existing_project
        task_repository.save.return_value = None
        role_id = uuid4()

        input_data = CreateTaskInput(
            project_id=existing_project.id,
            requester_id=manager_id,
            title="Backend task",
            required_role_id=role_id,
        )

        result = await use_case.execute(input_data)

        assert result.required_role_id == role_id

    @pytest.mark.asyncio
    async def test_raises_project_not_found_when_project_does_not_exist(
        self, use_case, project_repository, task_repository
    ):
        """Should raise ProjectNotFoundError when project doesn't exist."""
        project_repository.find_by_id.return_value = None

        input_data = CreateTaskInput(
            project_id=uuid4(),
            requester_id=uuid4(),
            title="Test task",
        )

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(input_data)

        task_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_manager_required_when_requester_is_not_manager(
        self, use_case, project_repository, task_repository, existing_project
    ):
        """BR-TASK-001: Only the Manager can create Tasks."""
        project_repository.find_by_id.return_value = existing_project
        non_manager_id = uuid4()

        input_data = CreateTaskInput(
            project_id=existing_project.id,
            requester_id=non_manager_id,
            title="Test task",
        )

        with pytest.raises(ManagerRequiredError):
            await use_case.execute(input_data)

        task_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_saves_task_to_repository(
        self,
        use_case,
        project_repository,
        task_repository,
        existing_project,
        manager_id,
    ):
        """Should save the task using the repository."""
        project_repository.find_by_id.return_value = existing_project
        task_repository.save.return_value = None

        input_data = CreateTaskInput(
            project_id=existing_project.id,
            requester_id=manager_id,
            title="Test task",
        )

        await use_case.execute(input_data)

        task_repository.save.assert_called_once()
        saved_task = task_repository.save.call_args[0][0]
        assert isinstance(saved_task, Task)
        assert saved_task.title == "Test task"
