"""Tests for SelectTaskUseCase."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.task_management import (
    SelectTaskInput,
    SelectTaskUseCase,
)
from backend.src.domain.entities import (
    Project,
    ProjectMember,
    SeniorityLevel,
    Task,
    TaskStatus,
)
from backend.src.domain.errors import (
    ProjectAccessDeniedError,
    ProjectNotFoundError,
    TaskNotFoundError,
    TaskNotSelectableError,
    WorkloadExceededError,
)


@pytest.fixture
def project_repository():
    return AsyncMock()


@pytest.fixture
def project_member_repository():
    return AsyncMock()


@pytest.fixture
def task_repository():
    return AsyncMock()


@pytest.fixture
def use_case(project_repository, project_member_repository, task_repository):
    return SelectTaskUseCase(
        project_repository=project_repository,
        project_member_repository=project_member_repository,
        task_repository=task_repository,
    )


@pytest.fixture
def manager_id():
    return uuid4()


@pytest.fixture
def existing_project(manager_id):
    return Project(name="Test Project", manager_id=manager_id)


@pytest.fixture
def member_user_id():
    return uuid4()


@pytest.fixture
def role_id():
    return uuid4()


@pytest.fixture
def project_member(existing_project, member_user_id, role_id):
    return ProjectMember(
        project_id=existing_project.id,
        user_id=member_user_id,
        role_id=role_id,
        seniority_level=SeniorityLevel.MID,
    )


@pytest.fixture
def todo_task(existing_project, role_id):
    return Task(
        project_id=existing_project.id,
        title="Test Task",
        difficulty_points=5,
        required_role_id=role_id,
    )


class TestSelectTaskUseCase:
    """Tests for SelectTaskUseCase.execute()."""

    @pytest.mark.asyncio
    async def test_selects_task_successfully(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        existing_project,
        project_member,
        todo_task,
        member_user_id,
    ):
        """BR-ASSIGN-001: Employees select tasks themselves."""
        project_repository.find_by_id.return_value = existing_project
        project_member_repository.find_by_project_and_user.return_value = project_member
        task_repository.find_by_id.return_value = todo_task
        task_repository.find_by_assignee.return_value = []
        task_repository.save.return_value = None

        input_data = SelectTaskInput(
            project_id=existing_project.id,
            task_id=todo_task.id,
            user_id=member_user_id,
        )

        result = await use_case.execute(input_data)

        assert result.status == TaskStatus.DOING
        assert result.assignee_id == project_member.id
        task_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_project_not_found(
        self, use_case, project_repository, project_member_repository, task_repository
    ):
        """Should raise ProjectNotFoundError when project doesn't exist."""
        project_repository.find_by_id.return_value = None

        input_data = SelectTaskInput(
            project_id=uuid4(),
            task_id=uuid4(),
            user_id=uuid4(),
        )

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_access_denied_when_not_member(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        existing_project,
    ):
        """Should raise ProjectAccessDeniedError when user is not a member."""
        project_repository.find_by_id.return_value = existing_project
        project_member_repository.find_by_project_and_user.return_value = None

        input_data = SelectTaskInput(
            project_id=existing_project.id,
            task_id=uuid4(),
            user_id=uuid4(),
        )

        with pytest.raises(ProjectAccessDeniedError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_task_not_found(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        existing_project,
        project_member,
        member_user_id,
    ):
        """Should raise TaskNotFoundError when task doesn't exist."""
        project_repository.find_by_id.return_value = existing_project
        project_member_repository.find_by_project_and_user.return_value = project_member
        task_repository.find_by_id.return_value = None

        input_data = SelectTaskInput(
            project_id=existing_project.id,
            task_id=uuid4(),
            user_id=member_user_id,
        )

        with pytest.raises(TaskNotFoundError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_task_not_selectable_without_difficulty(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        existing_project,
        project_member,
        member_user_id,
    ):
        """BR-TASK-004: Cannot select task without difficulty points."""
        task_without_difficulty = Task(
            project_id=existing_project.id,
            title="No difficulty task",
            difficulty_points=None,
        )
        project_repository.find_by_id.return_value = existing_project
        project_member_repository.find_by_project_and_user.return_value = project_member
        task_repository.find_by_id.return_value = task_without_difficulty

        input_data = SelectTaskInput(
            project_id=existing_project.id,
            task_id=task_without_difficulty.id,
            user_id=member_user_id,
        )

        with pytest.raises(TaskNotSelectableError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_task_not_selectable_wrong_status(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        existing_project,
        project_member,
        member_user_id,
    ):
        """Cannot select task that is not in Todo status."""
        doing_task = Task(
            project_id=existing_project.id,
            title="In progress task",
            difficulty_points=5,
        )
        doing_task.select(uuid4())  # Put in Doing status

        project_repository.find_by_id.return_value = existing_project
        project_member_repository.find_by_project_and_user.return_value = project_member
        task_repository.find_by_id.return_value = doing_task

        input_data = SelectTaskInput(
            project_id=existing_project.id,
            task_id=doing_task.id,
            user_id=member_user_id,
        )

        with pytest.raises(TaskNotSelectableError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_task_not_selectable_wrong_role(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        existing_project,
        project_member,
        member_user_id,
    ):
        """BR-ASSIGN-002: Only tasks matching Employee's Role can be selected."""
        different_role_id = uuid4()
        task_with_different_role = Task(
            project_id=existing_project.id,
            title="Different role task",
            difficulty_points=5,
            required_role_id=different_role_id,
        )
        project_repository.find_by_id.return_value = existing_project
        project_member_repository.find_by_project_and_user.return_value = project_member
        task_repository.find_by_id.return_value = task_with_different_role
        task_repository.find_by_assignee.return_value = []

        input_data = SelectTaskInput(
            project_id=existing_project.id,
            task_id=task_with_different_role.id,
            user_id=member_user_id,
        )

        with pytest.raises(TaskNotSelectableError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_raises_workload_exceeded(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        existing_project,
        project_member,
        todo_task,
        member_user_id,
    ):
        """BR-ASSIGN-003: Cannot select if workload would exceed Impossible threshold."""
        # Create tasks that already exceed workload (MID level has 10 capacity)
        existing_tasks = [
            Task(
                project_id=existing_project.id,
                title=f"Existing task {i}",
                difficulty_points=5,
                status=TaskStatus.DOING,
            )
            for i in range(4)  # 4 * 5 = 20 points, ratio = 2.0 > 1.5
        ]

        project_repository.find_by_id.return_value = existing_project
        project_member_repository.find_by_project_and_user.return_value = project_member
        task_repository.find_by_id.return_value = todo_task
        task_repository.find_by_assignee.return_value = existing_tasks

        input_data = SelectTaskInput(
            project_id=existing_project.id,
            task_id=todo_task.id,
            user_id=member_user_id,
        )

        with pytest.raises(WorkloadExceededError):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_allows_selection_within_workload_limit(
        self,
        use_case,
        project_repository,
        project_member_repository,
        task_repository,
        existing_project,
        project_member,
        todo_task,
        member_user_id,
    ):
        """Should allow selection when workload is within limits."""
        # Create tasks that are within healthy workload
        existing_tasks = [
            Task(
                project_id=existing_project.id,
                title="Existing task",
                difficulty_points=3,
                status=TaskStatus.DOING,
            )
        ]  # 3 points, adding 5 = 8 points, ratio = 0.8 < 1.5

        project_repository.find_by_id.return_value = existing_project
        project_member_repository.find_by_project_and_user.return_value = project_member
        task_repository.find_by_id.return_value = todo_task
        task_repository.find_by_assignee.return_value = existing_tasks
        task_repository.save.return_value = None

        input_data = SelectTaskInput(
            project_id=existing_project.id,
            task_id=todo_task.id,
            user_id=member_user_id,
        )

        result = await use_case.execute(input_data)

        assert result.status == TaskStatus.DOING
