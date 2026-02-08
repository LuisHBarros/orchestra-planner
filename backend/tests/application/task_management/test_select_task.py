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
    ProjectConfig,
    ProjectMember,
    SeniorityLevel,
    Task,
    TaskDependency,
    TaskLog,
    TaskLogType,
    TaskStatus,
)
from backend.src.domain.errors import (
    ManagerRequiredError,
    ProjectAccessDeniedError,
    ProjectNotFoundError,
    TaskNotFoundError,
    TaskNotSelectableError,
    WorkloadExceededError,
)


@pytest.fixture
def uow():
    mock = AsyncMock()
    mock.project_repository = AsyncMock()
    mock.project_member_repository = AsyncMock()
    mock.task_repository = AsyncMock()
    mock.task_log_repository = AsyncMock()
    mock.task_dependency_repository = AsyncMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=False)
    return mock


@pytest.fixture
def use_case(uow):
    return SelectTaskUseCase(uow=uow)


@pytest.fixture
def use_case_with_multitasking(uow):
    """Use case with multitasking enabled."""
    config = ProjectConfig(allow_multitasking=True)
    return SelectTaskUseCase(uow=uow, config=config)


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
def manager_member(existing_project, manager_id, role_id):
    """Manager as project member."""
    return ProjectMember(
        project_id=existing_project.id,
        user_id=manager_id,
        role_id=role_id,
        seniority_level=SeniorityLevel.LEAD,
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
        uow,
        existing_project,
        project_member,
        todo_task,
        member_user_id,
    ):
        """BR-ASSIGN-001: Employees select tasks themselves."""
        uow.project_repository.find_by_id.return_value = existing_project
        uow.project_member_repository.find_by_project_and_user.return_value = (
            project_member
        )
        uow.task_repository.find_by_id.return_value = todo_task
        uow.task_repository.find_by_assignee.return_value = []
        uow.task_repository.find_by_project.return_value = [todo_task]
        uow.task_dependency_repository.find_by_project.return_value = []
        uow.task_repository.save.return_value = None
        uow.task_log_repository.save.return_value = None

        input_data = SelectTaskInput(
            project_id=existing_project.id,
            task_id=todo_task.id,
            user_id=member_user_id,
        )

        result = await use_case.execute(input_data)

        assert result.status == TaskStatus.DOING
        assert result.assignee_id == project_member.id
        uow.task_repository.save.assert_called_once()
        uow.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_creates_assignment_log(
        self,
        use_case,
        uow,
        existing_project,
        project_member,
        todo_task,
        member_user_id,
    ):
        """BR-ASSIGN-005: All assignments are logged in history."""
        uow.project_repository.find_by_id.return_value = existing_project
        uow.project_member_repository.find_by_project_and_user.return_value = (
            project_member
        )
        uow.task_repository.find_by_id.return_value = todo_task
        uow.task_repository.find_by_assignee.return_value = []
        uow.task_repository.find_by_project.return_value = [todo_task]
        uow.task_dependency_repository.find_by_project.return_value = []
        uow.task_repository.save.return_value = None
        uow.task_log_repository.save.return_value = None

        input_data = SelectTaskInput(
            project_id=existing_project.id,
            task_id=todo_task.id,
            user_id=member_user_id,
        )

        await use_case.execute(input_data)

        uow.task_log_repository.save.assert_called_once()
        saved_log = uow.task_log_repository.save.call_args[0][0]
        assert isinstance(saved_log, TaskLog)
        assert saved_log.log_type == TaskLogType.ASSIGN
        assert saved_log.task_id == todo_task.id
        assert saved_log.author_id == project_member.id

    @pytest.mark.asyncio
    async def test_raises_project_not_found(
        self,
        use_case,
        uow,
    ):
        """Should raise ProjectNotFoundError when project doesn't exist."""
        uow.project_repository.find_by_id.return_value = None

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
        uow,
        existing_project,
    ):
        """Should raise ProjectAccessDeniedError when user is not a member."""
        uow.project_repository.find_by_id.return_value = existing_project
        uow.project_member_repository.find_by_project_and_user.return_value = None

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
        uow,
        existing_project,
        project_member,
        member_user_id,
    ):
        """Should raise TaskNotFoundError when task doesn't exist."""
        uow.project_repository.find_by_id.return_value = existing_project
        uow.project_member_repository.find_by_project_and_user.return_value = (
            project_member
        )
        uow.task_repository.find_by_id.return_value = None

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
        uow,
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
        uow.project_repository.find_by_id.return_value = existing_project
        uow.project_member_repository.find_by_project_and_user.return_value = (
            project_member
        )
        uow.task_repository.find_by_id.return_value = task_without_difficulty
        uow.task_repository.find_by_assignee.return_value = []
        uow.task_repository.find_by_project.return_value = [task_without_difficulty]
        uow.task_dependency_repository.find_by_project.return_value = []

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
        uow,
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

        uow.project_repository.find_by_id.return_value = existing_project
        uow.project_member_repository.find_by_project_and_user.return_value = (
            project_member
        )
        uow.task_repository.find_by_id.return_value = doing_task
        uow.task_repository.find_by_assignee.return_value = []
        uow.task_repository.find_by_project.return_value = [doing_task]
        uow.task_dependency_repository.find_by_project.return_value = []

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
        uow,
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
        uow.project_repository.find_by_id.return_value = existing_project
        uow.project_member_repository.find_by_project_and_user.return_value = (
            project_member
        )
        uow.task_repository.find_by_id.return_value = task_with_different_role
        uow.task_repository.find_by_assignee.return_value = []
        uow.task_repository.find_by_project.return_value = [task_with_different_role]
        uow.task_dependency_repository.find_by_project.return_value = []

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
        use_case_with_multitasking,
        uow,
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

        uow.project_repository.find_by_id.return_value = existing_project
        uow.project_member_repository.find_by_project_and_user.return_value = (
            project_member
        )
        uow.task_repository.find_by_id.return_value = todo_task
        uow.task_repository.find_by_assignee.return_value = existing_tasks
        uow.task_repository.find_by_project.return_value = existing_tasks + [todo_task]
        uow.task_dependency_repository.find_by_project.return_value = []

        input_data = SelectTaskInput(
            project_id=existing_project.id,
            task_id=todo_task.id,
            user_id=member_user_id,
        )

        with pytest.raises(WorkloadExceededError):
            await use_case_with_multitasking.execute(input_data)

    @pytest.mark.asyncio
    async def test_allows_selection_within_workload_limit(
        self,
        use_case_with_multitasking,
        uow,
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

        uow.project_repository.find_by_id.return_value = existing_project
        uow.project_member_repository.find_by_project_and_user.return_value = (
            project_member
        )
        uow.task_repository.find_by_id.return_value = todo_task
        uow.task_repository.find_by_assignee.return_value = existing_tasks
        uow.task_repository.find_by_project.return_value = existing_tasks + [todo_task]
        uow.task_dependency_repository.find_by_project.return_value = []
        uow.task_repository.save.return_value = None
        uow.task_log_repository.save.return_value = None

        input_data = SelectTaskInput(
            project_id=existing_project.id,
            task_id=todo_task.id,
            user_id=member_user_id,
        )

        result = await use_case_with_multitasking.execute(input_data)

        assert result.status == TaskStatus.DOING


class TestSelectTaskUseCaseManagerRestriction:
    """Tests for BR-PROJ-002: Manager cannot select tasks."""

    @pytest.mark.asyncio
    async def test_manager_cannot_select_task(
        self,
        use_case,
        uow,
        existing_project,
        manager_member,
        todo_task,
        manager_id,
    ):
        """BR-PROJ-002: Manager cannot be assigned tasks."""
        uow.project_repository.find_by_id.return_value = existing_project
        uow.project_member_repository.find_by_project_and_user.return_value = (
            manager_member
        )
        uow.task_repository.find_by_id.return_value = todo_task
        uow.task_repository.find_by_assignee.return_value = []
        uow.task_repository.find_by_project.return_value = [todo_task]
        uow.task_dependency_repository.find_by_project.return_value = []

        input_data = SelectTaskInput(
            project_id=existing_project.id,
            task_id=todo_task.id,
            user_id=manager_id,
        )

        with pytest.raises(ManagerRequiredError):
            await use_case.execute(input_data)


class TestSelectTaskUseCaseDependencies:
    """Tests for BR-DEP-001/003: Dependencies must be satisfied."""

    @pytest.mark.asyncio
    async def test_cannot_select_task_with_unfinished_dependencies(
        self,
        use_case,
        uow,
        existing_project,
        project_member,
        member_user_id,
    ):
        """BR-DEP-001: Cannot select task with unfinished dependencies."""
        blocking_task = Task(
            project_id=existing_project.id,
            title="Blocking Task",
            difficulty_points=3,
        )  # Status is TODO (not DONE)

        blocked_task = Task(
            project_id=existing_project.id,
            title="Blocked Task",
            difficulty_points=5,
        )

        dependency = TaskDependency(
            blocking_task_id=blocking_task.id,
            blocked_task_id=blocked_task.id,
        )

        uow.project_repository.find_by_id.return_value = existing_project
        uow.project_member_repository.find_by_project_and_user.return_value = (
            project_member
        )
        uow.task_repository.find_by_id.return_value = blocked_task
        uow.task_repository.find_by_assignee.return_value = []
        uow.task_repository.find_by_project.return_value = [
            blocking_task,
            blocked_task,
        ]
        uow.task_dependency_repository.find_by_project.return_value = [dependency]

        input_data = SelectTaskInput(
            project_id=existing_project.id,
            task_id=blocked_task.id,
            user_id=member_user_id,
        )

        with pytest.raises(TaskNotSelectableError, match="dependencies"):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_can_select_task_with_finished_dependencies(
        self,
        use_case,
        uow,
        existing_project,
        project_member,
        member_user_id,
    ):
        """Can select task when all dependencies are Done."""
        blocking_task = Task(
            project_id=existing_project.id,
            title="Blocking Task",
            difficulty_points=3,
        )
        blocking_task.select(uuid4())  # Move to DOING
        blocking_task.complete()  # Move to DONE

        blocked_task = Task(
            project_id=existing_project.id,
            title="Blocked Task",
            difficulty_points=5,
        )

        dependency = TaskDependency(
            blocking_task_id=blocking_task.id,
            blocked_task_id=blocked_task.id,
        )

        uow.project_repository.find_by_id.return_value = existing_project
        uow.project_member_repository.find_by_project_and_user.return_value = (
            project_member
        )
        uow.task_repository.find_by_id.return_value = blocked_task
        uow.task_repository.find_by_assignee.return_value = []
        uow.task_repository.find_by_project.return_value = [
            blocking_task,
            blocked_task,
        ]
        uow.task_dependency_repository.find_by_project.return_value = [dependency]
        uow.task_repository.save.return_value = None
        uow.task_log_repository.save.return_value = None

        input_data = SelectTaskInput(
            project_id=existing_project.id,
            task_id=blocked_task.id,
            user_id=member_user_id,
        )

        result = await use_case.execute(input_data)

        assert result.status == TaskStatus.DOING


class TestSelectTaskUseCaseSingleTaskFocus:
    """Tests for BR-ASSIGN-004: Single-task focus."""

    @pytest.mark.asyncio
    async def test_cannot_select_when_already_doing_task(
        self,
        use_case,
        uow,
        existing_project,
        project_member,
        todo_task,
        member_user_id,
    ):
        """BR-ASSIGN-004: Cannot select when already working on another task."""
        existing_doing_task = Task(
            project_id=existing_project.id,
            title="Already doing",
            difficulty_points=3,
        )
        existing_doing_task.select(project_member.id)

        uow.project_repository.find_by_id.return_value = existing_project
        uow.project_member_repository.find_by_project_and_user.return_value = (
            project_member
        )
        uow.task_repository.find_by_id.return_value = todo_task
        uow.task_repository.find_by_assignee.return_value = [existing_doing_task]
        uow.task_repository.find_by_project.return_value = [
            existing_doing_task,
            todo_task,
        ]
        uow.task_dependency_repository.find_by_project.return_value = []

        input_data = SelectTaskInput(
            project_id=existing_project.id,
            task_id=todo_task.id,
            user_id=member_user_id,
        )

        with pytest.raises(TaskNotSelectableError, match="another task"):
            await use_case.execute(input_data)

    @pytest.mark.asyncio
    async def test_can_select_when_multitasking_enabled(
        self,
        use_case_with_multitasking,
        uow,
        existing_project,
        project_member,
        todo_task,
        member_user_id,
    ):
        """Can select multiple tasks when multitasking is enabled."""
        existing_doing_task = Task(
            project_id=existing_project.id,
            title="Already doing",
            difficulty_points=3,
        )
        existing_doing_task.select(project_member.id)

        uow.project_repository.find_by_id.return_value = existing_project
        uow.project_member_repository.find_by_project_and_user.return_value = (
            project_member
        )
        uow.task_repository.find_by_id.return_value = todo_task
        uow.task_repository.find_by_assignee.return_value = [existing_doing_task]
        uow.task_repository.find_by_project.return_value = [
            existing_doing_task,
            todo_task,
        ]
        uow.task_dependency_repository.find_by_project.return_value = []
        uow.task_repository.save.return_value = None
        uow.task_log_repository.save.return_value = None

        input_data = SelectTaskInput(
            project_id=existing_project.id,
            task_id=todo_task.id,
            user_id=member_user_id,
        )

        result = await use_case_with_multitasking.execute(input_data)

        assert result.status == TaskStatus.DOING
