"""Tests for RecalculateProjectScheduleUseCase."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from backend.src.application.use_cases.project_management import (
    RecalculateProjectScheduleInput,
    RecalculateProjectScheduleUseCase,
)
from backend.src.domain.entities import (
    ProjectMember,
    Project,
    SeniorityLevel,
    Task,
    TaskDependency,
    TaskStatus,
    WorkingCalendar,
)
from backend.src.domain.services.schedule_calculator import (
    ProjectSchedule,
    ScheduleCalculator,
    TaskSchedule,
)


@pytest.fixture
def uow():
    mock = AsyncMock()
    mock.project_repository = AsyncMock()
    mock.project_member_repository = AsyncMock()
    mock.task_repository = AsyncMock()
    mock.task_dependency_repository = AsyncMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=False)
    return mock


@pytest.fixture
def schedule_calculator():
    return MagicMock(spec=ScheduleCalculator)


@pytest.fixture
def use_case(
    uow,
    schedule_calculator,
):
    return RecalculateProjectScheduleUseCase(
        uow=uow,
        schedule_calculator=schedule_calculator,
    )


@pytest.fixture
def project_id():
    return uuid4()


@pytest.fixture
def role_id():
    return uuid4()


@pytest.fixture
def member_id():
    return uuid4()


@pytest.fixture
def task_a(project_id):
    return Task(
        project_id=project_id,
        title="Task A",
        difficulty_points=2,
        status=TaskStatus.TODO,
    )


@pytest.fixture
def task_b(project_id, member_id):
    return Task(
        project_id=project_id,
        title="Task B",
        difficulty_points=3,
        status=TaskStatus.TODO,
        assignee_id=member_id,
    )


@pytest.fixture
def member(project_id, role_id, member_id):
    return ProjectMember(
        id=member_id,
        project_id=project_id,
        user_id=uuid4(),
        role_id=role_id,
        seniority_level=SeniorityLevel.SENIOR,
    )


@pytest.fixture
def dep(task_a, task_b):
    return TaskDependency(
        blocking_task_id=task_a.id,
        blocked_task_id=task_b.id,
    )


@pytest.fixture
def expected_schedule(task_a, task_b):
    start = datetime(2025, 2, 1, tzinfo=timezone.utc)
    end_a = datetime(2025, 2, 2, tzinfo=timezone.utc)
    end_b = datetime(2025, 2, 5, tzinfo=timezone.utc)
    return ProjectSchedule(
        task_schedules={
            task_a.id: TaskSchedule(
                task_id=task_a.id,
                expected_start_date=start,
                expected_end_date=end_a,
            ),
            task_b.id: TaskSchedule(
                task_id=task_b.id,
                expected_start_date=end_a,
                expected_end_date=end_b,
            ),
        },
        critical_path=[task_a.id, task_b.id],
        project_end_date=end_b,
    )


@pytest.fixture
def project(project_id):
    return Project(
        name="Project Schedule",
        manager_id=uuid4(),
        calendar=WorkingCalendar(timezone="UTC"),
        id=project_id,
    )


class TestRecalculateProjectScheduleUseCase:
    """Tests for RecalculateProjectScheduleUseCase.execute()."""

    @pytest.mark.asyncio
    async def test_returns_schedule_and_persists_task_dates_via_save_many(
        self,
        use_case,
        uow,
        schedule_calculator,
        project_id,
        task_a,
        task_b,
        dep,
        member,
        expected_schedule,
        project,
    ):
        """Recalculates schedule and batch-saves updated task dates."""
        tasks = [task_a, task_b]
        uow.task_repository.find_by_project.return_value = tasks
        uow.task_dependency_repository.find_by_project.return_value = [dep]
        uow.project_member_repository.find_by_project.return_value = [member]
        uow.project_repository.find_by_id.return_value = project
        schedule_calculator.calculate_schedule.return_value = expected_schedule
        uow.task_repository.save_many.side_effect = lambda ts: ts

        input_data = RecalculateProjectScheduleInput(project_id=project_id)
        result = await use_case.execute(input_data)

        assert result == expected_schedule
        uow.task_repository.find_by_project.assert_called_once_with(project_id)
        uow.task_dependency_repository.find_by_project.assert_called_once_with(
            project_id
        )
        uow.project_member_repository.find_by_project.assert_called_once_with(
            project_id
        )
        uow.project_repository.find_by_id.assert_awaited_once_with(project_id)
        schedule_calculator.calculate_schedule.assert_called_once()
        call_kwargs = schedule_calculator.calculate_schedule.call_args[1]
        assert call_kwargs["tasks"] == tasks
        assert call_kwargs["dependencies"] == [dep]
        assert call_kwargs["working_calendar"] is not None
        assert call_kwargs["working_calendar"].timezone == "UTC"
        uow.task_repository.save_many.assert_awaited_once_with(tasks)
        uow.commit.assert_awaited_once()

        # Task dates updated from schedule
        assert (
            task_a.expected_start_date
            == expected_schedule.task_schedules[task_a.id].expected_start_date
        )
        assert (
            task_a.expected_end_date
            == expected_schedule.task_schedules[task_a.id].expected_end_date
        )
        assert (
            task_b.expected_start_date
            == expected_schedule.task_schedules[task_b.id].expected_start_date
        )
        assert (
            task_b.expected_end_date
            == expected_schedule.task_schedules[task_b.id].expected_end_date
        )

    @pytest.mark.asyncio
    async def test_uses_default_seniority_for_unassigned_tasks(
        self,
        use_case,
        uow,
        schedule_calculator,
        project_id,
        task_a,
        expected_schedule,
        project,
    ):
        """Unassigned tasks use default_seniority from input."""
        uow.task_repository.find_by_project.return_value = [task_a]
        uow.task_dependency_repository.find_by_project.return_value = []
        uow.project_member_repository.find_by_project.return_value = []
        uow.project_repository.find_by_id.return_value = project
        schedule_calculator.calculate_schedule.return_value = expected_schedule
        uow.task_repository.save_many.side_effect = lambda ts: ts

        input_data = RecalculateProjectScheduleInput(
            project_id=project_id,
            default_seniority=SeniorityLevel.JUNIOR,
        )
        await use_case.execute(input_data)

        call_kwargs = schedule_calculator.calculate_schedule.call_args[1]
        assert (
            call_kwargs["assignee_seniority"][task_a.id]
            == SeniorityLevel.JUNIOR
        )

    @pytest.mark.asyncio
    async def test_uses_member_seniority_for_assigned_tasks(
        self,
        use_case,
        uow,
        schedule_calculator,
        project_id,
        task_b,
        member,
        expected_schedule,
        project,
    ):
        """Assigned tasks use their assignee's seniority from project members."""
        uow.task_repository.find_by_project.return_value = [task_b]
        uow.task_dependency_repository.find_by_project.return_value = []
        uow.project_member_repository.find_by_project.return_value = [member]
        uow.project_repository.find_by_id.return_value = project
        schedule_calculator.calculate_schedule.return_value = expected_schedule
        uow.task_repository.save_many.side_effect = lambda ts: ts

        input_data = RecalculateProjectScheduleInput(project_id=project_id)
        await use_case.execute(input_data)

        call_kwargs = schedule_calculator.calculate_schedule.call_args[1]
        assert (
            call_kwargs["assignee_seniority"][task_b.id]
            == SeniorityLevel.SENIOR
        )

    @pytest.mark.asyncio
    async def test_empty_project_returns_empty_schedule_no_save_many(
        self,
        use_case,
        uow,
        schedule_calculator,
        project_id,
    ):
        """No tasks yields empty schedule and save_many is not called."""
        empty_schedule = ProjectSchedule()
        uow.task_repository.find_by_project.return_value = []
        uow.task_dependency_repository.find_by_project.return_value = []
        uow.project_member_repository.find_by_project.return_value = []
        uow.project_repository.find_by_id.return_value = None
        schedule_calculator.calculate_schedule.return_value = empty_schedule

        input_data = RecalculateProjectScheduleInput(project_id=project_id)
        result = await use_case.execute(input_data)

        assert result == empty_schedule
        call_kwargs = schedule_calculator.calculate_schedule.call_args[1]
        assert call_kwargs["working_calendar"] is None
        uow.task_repository.save_many.assert_not_awaited()
        uow.commit.assert_not_awaited()
