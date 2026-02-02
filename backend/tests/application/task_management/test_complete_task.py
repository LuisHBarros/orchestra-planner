"""Tests for CompleteTaskUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.task_management import (
    CompleteTaskInput,
    CompleteTaskUseCase,
)
from backend.src.domain.entities import (
    Project,
    ProjectMember,
    SeniorityLevel,
    Task,
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
def use_case(project_member_repository, task_repository):
    return CompleteTaskUseCase(
        project_member_repository=project_member_repository,
        task_repository=task_repository,
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


class TestCompleteTaskUseCase:
    """Tests for CompleteTaskUseCase.execute()."""

    @pytest.mark.asyncio
    async def test_completes_task_successfully(
        self,
        use_case,
        project_member_repository,
        task_repository,
        project_member,
        doing_task,
        member_user_id,
    ):
        """Owner can complete their task."""
        task_repository.find_by_id.return_value = doing_task
        project_member_repository.find_by_project_and_user.return_value = project_member
        task_repository.save.return_value = None

        input_data = CompleteTaskInput(
            task_id=doing_task.id,
            user_id=member_user_id,
        )

        result = await use_case.execute(input_data)

        assert result.status == TaskStatus.DONE
        assert result.progress_percent == 100
        assert result.actual_end_date is not None
        task_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_task_not_found(
        self, use_case, project_member_repository, task_repository
    ):
        """Should raise TaskNotFoundError when task doesn't exist."""
        task_repository.find_by_id.return_value = None

        input_data = CompleteTaskInput(
            task_id=uuid4(),
            user_id=uuid4(),
        )

        with pytest.raises(TaskNotFoundError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_task_not_owned_when_not_assigned(
        self, use_case, project_member_repository, task_repository, project_id
    ):
        """Should raise TaskNotOwnedError when task has no assignee."""
        unassigned_task = Task(
            project_id=project_id,
            title="Unassigned task",
            difficulty_points=5,
        )
        task_repository.find_by_id.return_value = unassigned_task

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
        project_member_repository,
        task_repository,
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
        project_member_repository,
        task_repository,
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
        project_member_repository,
        task_repository,
        project_member,
        doing_task,
        member_user_id,
    ):
        """Should save the task after completion."""
        task_repository.find_by_id.return_value = doing_task
        project_member_repository.find_by_project_and_user.return_value = project_member
        task_repository.save.return_value = None

        input_data = CompleteTaskInput(
            task_id=doing_task.id,
            user_id=member_user_id,
        )

        await use_case.execute(input_data)

        task_repository.save.assert_called_once()
        saved_task = task_repository.save.call_args[0][0]
        assert saved_task.status == TaskStatus.DONE
