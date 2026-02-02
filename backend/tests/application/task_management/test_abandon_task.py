"""Tests for AbandonTaskUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.task_management import (
    AbandonTaskInput,
    AbandonTaskUseCase,
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
    return AbandonTaskUseCase(
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
    task.select(project_member.id)  # Put in Doing status with assignee
    return task


class TestAbandonTaskUseCase:
    """Tests for AbandonTaskUseCase.execute()."""

    @pytest.mark.asyncio
    async def test_abandons_task_successfully(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
        project_member,
        doing_task,
        member_user_id,
    ):
        """Owner can abandon their task with a reason."""
        task_repository.find_by_id.return_value = doing_task
        project_member_repository.find_by_project_and_user.return_value = project_member
        task_repository.save.return_value = None
        task_log_repository.save.return_value = None

        input_data = AbandonTaskInput(
            task_id=doing_task.id,
            user_id=member_user_id,
            reason="Blocked by external dependency",
        )

        result = await use_case.execute(input_data)

        assert result.status == TaskStatus.TODO
        assert result.assignee_id is None
        task_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_creates_abandon_log_with_reason(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
        project_member,
        doing_task,
        member_user_id,
    ):
        """BR-ABANDON-002: Creates audit log with abandonment reason."""
        task_repository.find_by_id.return_value = doing_task
        project_member_repository.find_by_project_and_user.return_value = project_member
        task_repository.save.return_value = None
        task_log_repository.save.return_value = None

        reason = "Need to focus on higher priority task"
        input_data = AbandonTaskInput(
            task_id=doing_task.id,
            user_id=member_user_id,
            reason=reason,
        )

        await use_case.execute(input_data)

        task_log_repository.save.assert_called_once()
        saved_log = task_log_repository.save.call_args[0][0]
        assert isinstance(saved_log, TaskLog)
        assert saved_log.log_type == TaskLogType.ABANDON
        assert saved_log.content == reason
        assert saved_log.task_id == doing_task.id
        assert saved_log.author_id == project_member.id

    @pytest.mark.asyncio
    async def test_raises_value_error_when_reason_is_empty(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
    ):
        """BR-ABANDON-002: Should raise ValueError when reason is empty."""
        input_data = AbandonTaskInput(
            task_id=uuid4(),
            user_id=uuid4(),
            reason="",
        )

        with pytest.raises(ValueError, match="Abandonment reason is required"):
            await use_case.execute(input_data)

        task_repository.find_by_id.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_value_error_when_reason_is_whitespace(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
    ):
        """BR-ABANDON-002: Should raise ValueError when reason is only whitespace."""
        input_data = AbandonTaskInput(
            task_id=uuid4(),
            user_id=uuid4(),
            reason="   ",
        )

        with pytest.raises(ValueError, match="Abandonment reason is required"):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_task_not_found(
        self, use_case, project_member_repository, task_repository, task_log_repository
    ):
        """Should raise TaskNotFoundError when task doesn't exist."""
        task_repository.find_by_id.return_value = None

        input_data = AbandonTaskInput(
            task_id=uuid4(),
            user_id=uuid4(),
            reason="Valid reason",
        )

        with pytest.raises(TaskNotFoundError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_task_not_owned_when_not_assigned(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
        project_id,
    ):
        """Should raise TaskNotOwnedError when task has no assignee."""
        unassigned_task = Task(
            project_id=project_id,
            title="Unassigned task",
            difficulty_points=5,
        )
        task_repository.find_by_id.return_value = unassigned_task

        input_data = AbandonTaskInput(
            task_id=unassigned_task.id,
            user_id=uuid4(),
            reason="Valid reason",
        )

        with pytest.raises(TaskNotOwnedError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_task_not_owned_when_different_user(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
        doing_task,
    ):
        """Should raise TaskNotOwnedError when user doesn't own the task."""
        different_user_id = uuid4()
        different_member = ProjectMember(
            project_id=doing_task.project_id,
            user_id=different_user_id,
            role_id=uuid4(),
            seniority_level=SeniorityLevel.MID,
        )
        task_repository.find_by_id.return_value = doing_task
        project_member_repository.find_by_project_and_user.return_value = (
            different_member
        )

        input_data = AbandonTaskInput(
            task_id=doing_task.id,
            user_id=different_user_id,
            reason="Valid reason",
        )

        with pytest.raises(TaskNotOwnedError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_value_error_when_task_not_in_doing_status(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
        project_id,
        project_member,
        member_user_id,
    ):
        """Should raise ValueError when task is not in Doing status."""
        todo_task = Task(
            project_id=project_id,
            title="Todo task",
            difficulty_points=5,
        )
        # Manually set assignee without changing status (simulating edge case)
        todo_task.assignee_id = project_member.id

        task_repository.find_by_id.return_value = todo_task
        project_member_repository.find_by_project_and_user.return_value = project_member

        input_data = AbandonTaskInput(
            task_id=todo_task.id,
            user_id=member_user_id,
            reason="Valid reason",
        )

        with pytest.raises(
            ValueError, match="Can only abandon tasks that are in progress"
        ):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_task_can_be_selected_again_after_abandonment(
        self,
        use_case,
        project_member_repository,
        task_repository,
        task_log_repository,
        project_member,
        doing_task,
        member_user_id,
    ):
        """Abandoned task should be selectable again."""
        task_repository.find_by_id.return_value = doing_task
        project_member_repository.find_by_project_and_user.return_value = project_member
        task_repository.save.return_value = None
        task_log_repository.save.return_value = None

        input_data = AbandonTaskInput(
            task_id=doing_task.id,
            user_id=member_user_id,
            reason="Need to reprioritize",
        )

        result = await use_case.execute(input_data)

        # Verify task can be selected again
        assert result.can_be_selected() is True
