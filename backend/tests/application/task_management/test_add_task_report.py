"""Tests for AddTaskReportUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.task_management import (
    AddTaskReportInput,
    AddTaskReportUseCase,
)
from backend.src.domain.entities import (
    ProjectMember,
    SeniorityLevel,
    Task,
    TaskLog,
    TaskLogType,
    TaskStatus,
)
from backend.src.domain.errors import TaskNotFoundError, TaskNotOwnedError


@pytest.fixture
def project_member_repository():
    return AsyncMock()


@pytest.fixture
def task_repository():
    return AsyncMock()


@pytest.fixture
def task_log_repository():
    return AsyncMock()


@pytest.fixture
def use_case(project_member_repository, task_repository, task_log_repository):
    return AddTaskReportUseCase(
        project_member_repository=project_member_repository,
        task_repository=task_repository,
        task_log_repository=task_log_repository,
    )


@pytest.fixture
def project_id():
    return uuid4()


@pytest.fixture
def member_user_id():
    return uuid4()


@pytest.fixture
def role_id():
    return uuid4()


@pytest.fixture
def project_member(project_id, member_user_id, role_id):
    return ProjectMember(
        project_id=project_id,
        user_id=member_user_id,
        role_id=role_id,
        seniority_level=SeniorityLevel.MID,
    )


@pytest.fixture
def doing_task(project_id, project_member):
    task = Task(
        project_id=project_id,
        title="In progress task",
        difficulty_points=5,
    )
    task.select(project_member.id)
    return task


@pytest.fixture
def todo_task(project_id):
    return Task(
        project_id=project_id,
        title="Todo task",
        difficulty_points=3,
    )


class TestAddTaskReportUseCase:
    """Tests for AddTaskReportUseCase.execute()."""

    @pytest.mark.asyncio
    async def test_adds_report_successfully(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
        project_member,
        doing_task,
        member_user_id,
    ):
        """Owner can add a progress report to their task."""
        task_repository.find_by_id.return_value = doing_task
        project_member_repository.find_by_project_and_user.return_value = project_member
        task_log_repository.save.return_value = None

        input_data = AddTaskReportInput(
            task_id=doing_task.id,
            user_id=member_user_id,
            report_text="Fixed the login bug, now testing edge cases",
        )

        result = await use_case.execute(input_data)

        assert isinstance(result, TaskLog)
        assert result.log_type == TaskLogType.REPORT
        assert result.task_id == doing_task.id
        assert result.author_id == project_member.id
        task_log_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_report_content_is_preserved(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
        project_member,
        doing_task,
        member_user_id,
    ):
        """Report text content should be saved correctly."""
        task_repository.find_by_id.return_value = doing_task
        project_member_repository.find_by_project_and_user.return_value = project_member
        task_log_repository.save.return_value = None

        report_text = "Completed API integration. Still need to add error handling."
        input_data = AddTaskReportInput(
            task_id=doing_task.id,
            user_id=member_user_id,
            report_text=report_text,
        )

        result = await use_case.execute(input_data)

        assert result.content == report_text

    @pytest.mark.asyncio
    async def test_report_text_is_trimmed(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
        project_member,
        doing_task,
        member_user_id,
    ):
        """Report text should be trimmed of leading/trailing whitespace."""
        task_repository.find_by_id.return_value = doing_task
        project_member_repository.find_by_project_and_user.return_value = project_member
        task_log_repository.save.return_value = None

        input_data = AddTaskReportInput(
            task_id=doing_task.id,
            user_id=member_user_id,
            report_text="  Progress update with whitespace  ",
        )

        result = await use_case.execute(input_data)

        assert result.content == "Progress update with whitespace"

    @pytest.mark.asyncio
    async def test_raises_value_error_when_report_empty(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
    ):
        """Should raise ValueError when report text is empty."""
        input_data = AddTaskReportInput(
            task_id=uuid4(),
            user_id=uuid4(),
            report_text="",
        )

        with pytest.raises(ValueError, match="Report text cannot be empty"):
            await use_case.execute(input_data)

        task_repository.find_by_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_value_error_when_report_is_whitespace(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
    ):
        """Should raise ValueError when report text is only whitespace."""
        input_data = AddTaskReportInput(
            task_id=uuid4(),
            user_id=uuid4(),
            report_text="   ",
        )

        with pytest.raises(ValueError, match="Report text cannot be empty"):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_task_not_found(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
    ):
        """Should raise TaskNotFoundError when task doesn't exist."""
        task_repository.find_by_id.return_value = None

        input_data = AddTaskReportInput(
            task_id=uuid4(),
            user_id=uuid4(),
            report_text="Valid report text",
        )

        with pytest.raises(TaskNotFoundError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_value_error_when_task_not_in_doing_status(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
        todo_task,
        member_user_id,
    ):
        """Should raise ValueError when task is not in Doing status."""
        task_repository.find_by_id.return_value = todo_task

        input_data = AddTaskReportInput(
            task_id=todo_task.id,
            user_id=member_user_id,
            report_text="Valid report text",
        )

        with pytest.raises(ValueError, match="Task must be in Doing status"):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_task_not_owned_when_not_assigned(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
        project_id,
        project_member,
        member_user_id,
    ):
        """Should raise TaskNotOwnedError when task has no assignee."""
        # Create a task manually in Doing status but without assignee (edge case)
        unassigned_task = Task(
            project_id=project_id,
            title="Unassigned Doing task",
            difficulty_points=5,
        )
        unassigned_task.select(project_member.id)
        unassigned_task.assignee_id = None  # Simulate edge case

        task_repository.find_by_id.return_value = unassigned_task

        input_data = AddTaskReportInput(
            task_id=unassigned_task.id,
            user_id=member_user_id,
            report_text="Valid report text",
        )

        with pytest.raises(TaskNotOwnedError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_task_not_owned_when_user_not_member(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
        doing_task,
    ):
        """Should raise TaskNotOwnedError when user is not a project member."""
        task_repository.find_by_id.return_value = doing_task
        project_member_repository.find_by_project_and_user.return_value = None
        random_user_id = uuid4()

        input_data = AddTaskReportInput(
            task_id=doing_task.id,
            user_id=random_user_id,
            report_text="Valid report text",
        )

        with pytest.raises(TaskNotOwnedError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_task_not_owned_when_different_assignee(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
        doing_task,
        project_id,
        role_id,
    ):
        """Should raise TaskNotOwnedError when user is not the task assignee."""
        different_user_id = uuid4()
        different_member = ProjectMember(
            project_id=project_id,
            user_id=different_user_id,
            role_id=role_id,
            seniority_level=SeniorityLevel.SENIOR,
        )

        task_repository.find_by_id.return_value = doing_task
        project_member_repository.find_by_project_and_user.return_value = (
            different_member
        )

        input_data = AddTaskReportInput(
            task_id=doing_task.id,
            user_id=different_user_id,
            report_text="Valid report text",
        )

        with pytest.raises(TaskNotOwnedError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_multiple_reports_can_be_added(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
        project_member,
        doing_task,
        member_user_id,
    ):
        """Multiple reports can be added to the same task."""
        task_repository.find_by_id.return_value = doing_task
        project_member_repository.find_by_project_and_user.return_value = project_member
        task_log_repository.save.return_value = None

        reports = [
            "Started working on the feature",
            "Completed initial implementation",
            "Fixed bugs found during testing",
        ]

        for report_text in reports:
            input_data = AddTaskReportInput(
                task_id=doing_task.id,
                user_id=member_user_id,
                report_text=report_text,
            )

            result = await use_case.execute(input_data)
            assert result.content == report_text

        assert task_log_repository.save.call_count == 3

    @pytest.mark.asyncio
    async def test_report_has_correct_log_type(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
        project_member,
        doing_task,
        member_user_id,
    ):
        """Report should have REPORT log type."""
        task_repository.find_by_id.return_value = doing_task
        project_member_repository.find_by_project_and_user.return_value = project_member
        task_log_repository.save.return_value = None

        input_data = AddTaskReportInput(
            task_id=doing_task.id,
            user_id=member_user_id,
            report_text="Progress update",
        )

        result = await use_case.execute(input_data)

        assert result.log_type == TaskLogType.REPORT
        # Verify it's not confused with other log types
        assert result.log_type != TaskLogType.ABANDON
        assert result.log_type != TaskLogType.ASSIGN
        assert result.log_type != TaskLogType.UNASSIGN
