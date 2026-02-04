"""Tests for RemoveFromTaskUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.task_management import (
    RemoveFromTaskInput,
    RemoveFromTaskUseCase,
)
from backend.src.domain.entities import (
    Project,
    ProjectMember,
    SeniorityLevel,
    Task,
    TaskLog,
    TaskLogType,
    TaskStatus,
)
from backend.src.domain.errors import (
    ManagerRequiredError,
    ProjectNotFoundError,
    TaskNotAssignedError,
    TaskNotFoundError,
)


@pytest.fixture
def project_repository():
    return AsyncMock()


@pytest.fixture
def task_repository():
    return AsyncMock()


@pytest.fixture
def task_log_repository():
    return AsyncMock()


@pytest.fixture
def use_case(project_repository, task_repository, task_log_repository):
    return RemoveFromTaskUseCase(
        project_repository=project_repository,
        task_repository=task_repository,
        task_log_repository=task_log_repository,
    )


@pytest.fixture
def manager_user_id():
    return uuid4()


@pytest.fixture
def employee_user_id():
    return uuid4()


@pytest.fixture
def project(manager_user_id):
    return Project(
        name="Test Project",
        manager_id=manager_user_id,
    )


@pytest.fixture
def role_id():
    return uuid4()


@pytest.fixture
def employee_member(project, employee_user_id, role_id):
    return ProjectMember(
        project_id=project.id,
        user_id=employee_user_id,
        role_id=role_id,
        seniority_level=SeniorityLevel.MID,
    )


@pytest.fixture
def doing_task(project, employee_member):
    task = Task(
        project_id=project.id,
        title="In progress task",
        difficulty_points=5,
    )
    task.select(employee_member.id)
    return task


@pytest.fixture
def todo_task(project):
    return Task(
        project_id=project.id,
        title="Todo task",
        difficulty_points=3,
    )


@pytest.fixture
def unassigned_doing_task(project, employee_member):
    """A task in Doing status but somehow unassigned (edge case)."""
    task = Task(
        project_id=project.id,
        title="Edge case task",
        difficulty_points=5,
    )
    task.select(employee_member.id)
    task.assignee_id = None  # Simulate edge case
    return task


class TestRemoveFromTaskUseCase:
    """Tests for RemoveFromTaskUseCase.execute()."""

    @pytest.mark.asyncio
    async def test_removes_employee_from_task_successfully(
        self,
        use_case,
        project_repository,
        task_repository,
        task_log_repository,
        project,
        doing_task,
        manager_user_id,
    ):
        """Manager can forcibly remove an employee from a task."""
        task_repository.find_by_id.return_value = doing_task
        project_repository.find_by_id.return_value = project
        task_repository.save.return_value = None
        task_log_repository.save.return_value = None

        input_data = RemoveFromTaskInput(
            task_id=doing_task.id,
            manager_user_id=manager_user_id,
        )

        result = await use_case.execute(input_data)

        assert result.status == TaskStatus.TODO
        assert result.assignee_id is None
        task_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_creates_unassignment_log(
        self,
        use_case,
        project_repository,
        task_repository,
        task_log_repository,
        project,
        doing_task,
        employee_member,
        manager_user_id,
    ):
        """BR-ASSIGN-005: Creates audit log for the unassignment."""
        task_repository.find_by_id.return_value = doing_task
        project_repository.find_by_id.return_value = project
        task_repository.save.return_value = None
        task_log_repository.save.return_value = None

        input_data = RemoveFromTaskInput(
            task_id=doing_task.id,
            manager_user_id=manager_user_id,
        )

        await use_case.execute(input_data)

        task_log_repository.save.assert_called_once()
        saved_log = task_log_repository.save.call_args[0][0]
        assert isinstance(saved_log, TaskLog)
        assert saved_log.log_type == TaskLogType.UNASSIGN
        assert saved_log.task_id == doing_task.id
        assert saved_log.author_id == employee_member.id
        assert "manager" in saved_log.content.lower()

    @pytest.mark.asyncio
    async def test_raises_task_not_found(
        self,
        use_case,
        project_repository,
        task_repository,
        task_log_repository,
        manager_user_id,
    ):
        """Should raise TaskNotFoundError when task doesn't exist."""
        task_repository.find_by_id.return_value = None

        input_data = RemoveFromTaskInput(
            task_id=uuid4(),
            manager_user_id=manager_user_id,
        )

        with pytest.raises(TaskNotFoundError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_project_not_found(
        self,
        use_case,
        project_repository,
        task_repository,
        task_log_repository,
        doing_task,
        manager_user_id,
    ):
        """Should raise ProjectNotFoundError when project doesn't exist."""
        task_repository.find_by_id.return_value = doing_task
        project_repository.find_by_id.return_value = None

        input_data = RemoveFromTaskInput(
            task_id=doing_task.id,
            manager_user_id=manager_user_id,
        )

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_manager_required_when_not_manager(
        self,
        use_case,
        project_repository,
        task_repository,
        task_log_repository,
        project,
        doing_task,
    ):
        """Should raise ManagerRequiredError when user is not the manager."""
        task_repository.find_by_id.return_value = doing_task
        project_repository.find_by_id.return_value = project
        non_manager_id = uuid4()

        input_data = RemoveFromTaskInput(
            task_id=doing_task.id,
            manager_user_id=non_manager_id,
        )

        with pytest.raises(ManagerRequiredError, match="remove employee from task"):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_task_not_assigned_when_no_assignee(
        self,
        use_case,
        project_repository,
        task_repository,
        task_log_repository,
        project,
        todo_task,
        manager_user_id,
    ):
        """Should raise TaskNotAssignedError when task has no assignee."""
        task_repository.find_by_id.return_value = todo_task
        project_repository.find_by_id.return_value = project

        input_data = RemoveFromTaskInput(
            task_id=todo_task.id,
            manager_user_id=manager_user_id,
        )

        with pytest.raises(TaskNotAssignedError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_value_error_when_task_not_in_doing_status(
        self,
        use_case,
        project_repository,
        task_repository,
        task_log_repository,
        project,
        employee_member,
        manager_user_id,
    ):
        """Should raise ValueError when task is not in Doing status."""
        # Create a blocked task with an assignee
        blocked_task = Task(
            project_id=project.id,
            title="Blocked task",
            difficulty_points=5,
        )
        blocked_task.select(employee_member.id)
        blocked_task.block()

        task_repository.find_by_id.return_value = blocked_task
        project_repository.find_by_id.return_value = project

        input_data = RemoveFromTaskInput(
            task_id=blocked_task.id,
            manager_user_id=manager_user_id,
        )

        with pytest.raises(ValueError, match="Task must be in Doing status"):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_task_can_be_selected_again_after_removal(
        self,
        use_case,
        project_repository,
        task_repository,
        task_log_repository,
        project,
        doing_task,
        manager_user_id,
    ):
        """Removed task should be selectable again."""
        task_repository.find_by_id.return_value = doing_task
        project_repository.find_by_id.return_value = project
        task_repository.save.return_value = None
        task_log_repository.save.return_value = None

        input_data = RemoveFromTaskInput(
            task_id=doing_task.id,
            manager_user_id=manager_user_id,
        )

        result = await use_case.execute(input_data)

        assert result.can_be_selected() is True

    @pytest.mark.asyncio
    async def test_employee_can_self_select_removed_task(
        self,
        use_case,
        project_repository,
        task_repository,
        task_log_repository,
        project,
        doing_task,
        employee_member,
        manager_user_id,
    ):
        """After removal, any employee (including the same one) can select the task."""
        task_repository.find_by_id.return_value = doing_task
        project_repository.find_by_id.return_value = project
        task_repository.save.return_value = None
        task_log_repository.save.return_value = None

        input_data = RemoveFromTaskInput(
            task_id=doing_task.id,
            manager_user_id=manager_user_id,
        )

        result = await use_case.execute(input_data)

        # Simulate the same employee selecting the task again
        result.select(employee_member.id)
        assert result.status == TaskStatus.DOING
        assert result.assignee_id == employee_member.id
