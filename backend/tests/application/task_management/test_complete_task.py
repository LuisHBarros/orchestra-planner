"""Tests for CompleteTaskUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.task_management import (
    CompleteTaskInput,
    CompleteTaskUseCase,
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
def uow():
    mock = AsyncMock()
    mock.project_member_repository = AsyncMock()
    mock.task_repository = AsyncMock()
    mock.task_log_repository = AsyncMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=False)
    return mock


@pytest.fixture
def use_case(uow):
    return CompleteTaskUseCase(uow=uow)


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


class TestCompleteTaskUseCase:
    """Tests for CompleteTaskUseCase.execute()."""

    @pytest.mark.asyncio
    async def test_completes_task_successfully(
        self,
        use_case,
        uow,
        project_member,
        doing_task,
        member_user_id,
    ):
        """Owner can complete their task."""
        uow.task_repository.find_by_id.return_value = doing_task
        uow.project_member_repository.find_by_project_and_user.return_value = (
            project_member
        )
        uow.task_repository.save.return_value = None
        uow.task_log_repository.save.return_value = None

        input_data = CompleteTaskInput(
            task_id=doing_task.id,
            user_id=member_user_id,
        )

        result = await use_case.execute(input_data)

        assert result.status == TaskStatus.DONE
        assert result.progress_percent == 100
        assert result.actual_end_date is not None
        uow.task_repository.save.assert_called_once()
        uow.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_creates_status_change_log(
        self,
        use_case,
        uow,
        project_member,
        doing_task,
        member_user_id,
    ):
        """BR-ASSIGN-005: All status changes are logged in history."""
        uow.task_repository.find_by_id.return_value = doing_task
        uow.project_member_repository.find_by_project_and_user.return_value = (
            project_member
        )
        uow.task_repository.save.return_value = None
        uow.task_log_repository.save.return_value = None

        input_data = CompleteTaskInput(
            task_id=doing_task.id,
            user_id=member_user_id,
        )

        await use_case.execute(input_data)

        uow.task_log_repository.save.assert_called_once()
        saved_log = uow.task_log_repository.save.call_args[0][0]
        assert isinstance(saved_log, TaskLog)
        assert saved_log.log_type == TaskLogType.STATUS_CHANGE
        assert saved_log.task_id == doing_task.id
        assert saved_log.author_id == project_member.id
        assert "Doing" in saved_log.content
        assert "Done" in saved_log.content

    @pytest.mark.asyncio
    async def test_raises_task_not_found(self, use_case, uow):
        """Should raise TaskNotFoundError when task doesn't exist."""
        uow.task_repository.find_by_id.return_value = None

        input_data = CompleteTaskInput(
            task_id=uuid4(),
            user_id=uuid4(),
        )

        with pytest.raises(TaskNotFoundError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_task_not_owned_when_not_assigned(
        self,
        use_case,
        uow,
        project_id,
    ):
        """Should raise TaskNotOwnedError when task has no assignee."""
        unassigned_task = Task(
            project_id=project_id,
            title="Unassigned task",
            difficulty_points=5,
        )
        uow.task_repository.find_by_id.return_value = unassigned_task

        input_data = CompleteTaskInput(
            task_id=unassigned_task.id,
            user_id=uuid4(),
        )

        with pytest.raises(TaskNotOwnedError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_task_not_owned_when_different_user(
        self,
        use_case,
        uow,
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
        uow.task_repository.find_by_id.return_value = doing_task
        uow.project_member_repository.find_by_project_and_user.return_value = (
            different_member
        )

        input_data = CompleteTaskInput(
            task_id=doing_task.id,
            user_id=different_user_id,
        )

        with pytest.raises(TaskNotOwnedError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_value_error_when_task_not_in_doing_status(
        self,
        use_case,
        uow,
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

        uow.task_repository.find_by_id.return_value = todo_task
        uow.project_member_repository.find_by_project_and_user.return_value = (
            project_member
        )

        input_data = CompleteTaskInput(
            task_id=todo_task.id,
            user_id=member_user_id,
        )

        with pytest.raises(
            ValueError, match="Can only complete tasks that are in progress"
        ):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_saves_completed_task(
        self,
        use_case,
        uow,
        project_member,
        doing_task,
        member_user_id,
    ):
        """Should save the task after completion."""
        uow.task_repository.find_by_id.return_value = doing_task
        uow.project_member_repository.find_by_project_and_user.return_value = (
            project_member
        )
        uow.task_repository.save.return_value = None
        uow.task_log_repository.save.return_value = None

        input_data = CompleteTaskInput(
            task_id=doing_task.id,
            user_id=member_user_id,
        )

        await use_case.execute(input_data)

        uow.task_repository.save.assert_called_once()
        saved_task = uow.task_repository.save.call_args[0][0]
        assert saved_task.status == TaskStatus.DONE
