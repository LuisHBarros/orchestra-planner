"""Tests for ScheduleCalculator domain service."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from backend.src.domain.entities import (
    SeniorityLevel,
    Task,
    TaskDependency,
    TaskStatus,
)
from backend.src.domain.services import ScheduleCalculator


@pytest.fixture
def calculator():
    return ScheduleCalculator()


@pytest.fixture
def project_id():
    return uuid4()


@pytest.fixture
def start_date():
    # Use a Monday to avoid weekend issues in tests
    return datetime(2024, 1, 8, 9, 0, 0, tzinfo=timezone.utc)


class TestScheduleCalculatorEstimateDuration:
    """Tests for ScheduleCalculator.estimate_duration_days()."""

    def test_estimates_duration_for_mid_level(self, calculator):
        """Mid-level (1.0x multiplier) should take standard time."""
        # 5 points / 2 points per day = 2.5 -> rounds to 2 days
        duration = calculator.estimate_duration_days(5, SeniorityLevel.MID)
        assert duration == 2

    def test_estimates_duration_for_senior(self, calculator):
        """Senior (1.3x multiplier) should be faster."""
        # 5 points / (2 * 1.3) = 5 / 2.6 = 1.92 -> 2 days
        duration = calculator.estimate_duration_days(5, SeniorityLevel.SENIOR)
        assert duration == 2

    def test_estimates_duration_for_junior(self, calculator):
        """Junior (0.6x multiplier) should be slower."""
        # 5 points / (2 * 0.6) = 5 / 1.2 = 4.17 -> 4 days
        duration = calculator.estimate_duration_days(5, SeniorityLevel.JUNIOR)
        assert duration == 4

    def test_returns_minimum_one_day_for_zero_points(self, calculator):
        """Should return at least 1 day for zero or no points."""
        assert calculator.estimate_duration_days(0) == 1
        assert calculator.estimate_duration_days(None) == 1

    def test_returns_minimum_one_day_for_small_tasks(self, calculator):
        """Should return at least 1 day for very small tasks."""
        assert calculator.estimate_duration_days(1, SeniorityLevel.SENIOR) >= 1


class TestScheduleCalculatorAddWorkingDays:
    """Tests for ScheduleCalculator._add_working_days()."""

    def test_adds_working_days_skipping_weekends(self, calculator, start_date):
        """Should skip weekends when adding days."""
        # Monday + 5 working days = Monday (next week)
        result = calculator._add_working_days(start_date, 5)
        assert result.weekday() == 0  # Monday

    def test_adds_single_working_day(self, calculator, start_date):
        """Adding 1 working day to Monday = Tuesday."""
        result = calculator._add_working_days(start_date, 1)
        assert result.weekday() == 1  # Tuesday

    def test_handles_friday_to_monday(self, calculator):
        """Adding 1 working day to Friday = Monday."""
        friday = datetime(2024, 1, 12, 9, 0, 0, tzinfo=timezone.utc)
        result = calculator._add_working_days(friday, 1)
        assert result.weekday() == 0  # Monday


class TestScheduleCalculatorTopologicalSort:
    """Tests for ScheduleCalculator._topological_sort()."""

    def test_sorts_tasks_with_no_dependencies(self, calculator, project_id):
        """Tasks with no dependencies can be in any order."""
        tasks = [
            Task(project_id=project_id, title="Task A", difficulty_points=3),
            Task(project_id=project_id, title="Task B", difficulty_points=5),
        ]
        result = calculator._topological_sort(tasks, [])
        assert len(result) == 2

    def test_sorts_tasks_with_linear_dependencies(self, calculator, project_id):
        """Tasks with linear dependencies should be sorted correctly."""
        task_a = Task(project_id=project_id, title="Task A", difficulty_points=3)
        task_b = Task(project_id=project_id, title="Task B", difficulty_points=5)
        task_c = Task(project_id=project_id, title="Task C", difficulty_points=2)

        dependencies = [
            TaskDependency(blocking_task_id=task_a.id, blocked_task_id=task_b.id),
            TaskDependency(blocking_task_id=task_b.id, blocked_task_id=task_c.id),
        ]

        result = calculator._topological_sort([task_a, task_b, task_c], dependencies)

        # A should come before B, B should come before C
        assert result.index(task_a.id) < result.index(task_b.id)
        assert result.index(task_b.id) < result.index(task_c.id)


class TestScheduleCalculatorCalculateSchedule:
    """Tests for ScheduleCalculator.calculate_schedule()."""

    def test_calculates_schedule_for_single_task(
        self, calculator, project_id, start_date
    ):
        """Should calculate schedule for a single task."""
        task = Task(project_id=project_id, title="Single Task", difficulty_points=4)

        schedule = calculator.calculate_schedule(
            tasks=[task],
            dependencies=[],
            project_start_date=start_date,
        )

        assert task.id in schedule.task_schedules
        task_schedule = schedule.task_schedules[task.id]
        assert task_schedule.expected_start_date == start_date
        assert task_schedule.expected_end_date > start_date

    def test_calculates_schedule_with_dependencies(
        self, calculator, project_id, start_date
    ):
        """Dependent tasks should start after their blocking tasks finish."""
        task_a = Task(project_id=project_id, title="Task A", difficulty_points=2)
        task_b = Task(project_id=project_id, title="Task B", difficulty_points=2)

        dependencies = [
            TaskDependency(blocking_task_id=task_a.id, blocked_task_id=task_b.id),
        ]

        schedule = calculator.calculate_schedule(
            tasks=[task_a, task_b],
            dependencies=dependencies,
            project_start_date=start_date,
        )

        # Task B should start after Task A ends
        schedule_a = schedule.task_schedules[task_a.id]
        schedule_b = schedule.task_schedules[task_b.id]
        assert schedule_b.expected_start_date >= schedule_a.expected_end_date

    def test_calculates_project_end_date(self, calculator, project_id, start_date):
        """Should calculate the overall project end date."""
        task_a = Task(project_id=project_id, title="Task A", difficulty_points=3)
        task_b = Task(project_id=project_id, title="Task B", difficulty_points=5)

        schedule = calculator.calculate_schedule(
            tasks=[task_a, task_b],
            dependencies=[],
            project_start_date=start_date,
        )

        assert schedule.project_end_date is not None
        assert schedule.project_end_date >= start_date

    def test_identifies_critical_path(self, calculator, project_id, start_date):
        """Should identify tasks on the critical path."""
        # Create a clear critical path: A -> B -> C (longer) vs D (shorter)
        task_a = Task(project_id=project_id, title="Task A", difficulty_points=5)
        task_b = Task(project_id=project_id, title="Task B", difficulty_points=5)
        task_c = Task(project_id=project_id, title="Task C", difficulty_points=5)
        task_d = Task(project_id=project_id, title="Task D", difficulty_points=2)

        # A -> B -> C is the critical path
        dependencies = [
            TaskDependency(blocking_task_id=task_a.id, blocked_task_id=task_b.id),
            TaskDependency(blocking_task_id=task_b.id, blocked_task_id=task_c.id),
        ]

        schedule = calculator.calculate_schedule(
            tasks=[task_a, task_b, task_c, task_d],
            dependencies=dependencies,
            project_start_date=start_date,
        )

        # Task D should have slack (not on critical path)
        # The chain A -> B -> C should be on critical path
        assert schedule.task_schedules[task_d.id].slack_days > 0
        # At minimum, check that schedule was calculated
        assert len(schedule.task_schedules) == 4

    def test_excludes_done_tasks(self, calculator, project_id, start_date):
        """Should not schedule tasks that are already done."""
        todo_task = Task(project_id=project_id, title="Todo", difficulty_points=3)
        done_task = Task(project_id=project_id, title="Done", difficulty_points=5)
        done_task.select(uuid4())
        done_task.complete()

        schedule = calculator.calculate_schedule(
            tasks=[todo_task, done_task],
            dependencies=[],
            project_start_date=start_date,
        )

        assert todo_task.id in schedule.task_schedules
        assert done_task.id not in schedule.task_schedules

    def test_excludes_cancelled_tasks(self, calculator, project_id, start_date):
        """Should not schedule tasks that are cancelled."""
        todo_task = Task(project_id=project_id, title="Todo", difficulty_points=3)
        cancelled_task = Task(
            project_id=project_id, title="Cancelled", difficulty_points=5
        )
        cancelled_task.cancel()

        schedule = calculator.calculate_schedule(
            tasks=[todo_task, cancelled_task],
            dependencies=[],
            project_start_date=start_date,
        )

        assert todo_task.id in schedule.task_schedules
        assert cancelled_task.id not in schedule.task_schedules

    def test_handles_empty_task_list(self, calculator):
        """Should handle empty task list gracefully."""
        schedule = calculator.calculate_schedule(tasks=[], dependencies=[])

        assert len(schedule.task_schedules) == 0
        assert schedule.project_end_date is None

    def test_uses_seniority_for_duration(self, calculator, project_id, start_date):
        """Should use assignee seniority for duration calculation."""
        task = Task(project_id=project_id, title="Task", difficulty_points=6)

        # Senior (1.3x) should be faster than default (Mid 1.0x)
        schedule_senior = calculator.calculate_schedule(
            tasks=[task],
            dependencies=[],
            project_start_date=start_date,
            assignee_seniority={task.id: SeniorityLevel.SENIOR},
        )

        task2 = Task(project_id=project_id, title="Task2", difficulty_points=6)
        schedule_junior = calculator.calculate_schedule(
            tasks=[task2],
            dependencies=[],
            project_start_date=start_date,
            assignee_seniority={task2.id: SeniorityLevel.JUNIOR},
        )

        senior_duration = (
            schedule_senior.task_schedules[task.id].expected_end_date
            - schedule_senior.task_schedules[task.id].expected_start_date
        )
        junior_duration = (
            schedule_junior.task_schedules[task2.id].expected_end_date
            - schedule_junior.task_schedules[task2.id].expected_start_date
        )

        assert senior_duration < junior_duration


class TestScheduleCalculatorRecalculateFromDelay:
    """Tests for ScheduleCalculator.recalculate_from_delay()."""

    def test_recalculates_dependent_tasks_when_delayed(
        self, calculator, project_id, start_date
    ):
        """BR-SCHED-001: If a task is delayed, dependent tasks are recalculated."""
        task_a = Task(project_id=project_id, title="Task A", difficulty_points=2)
        task_b = Task(project_id=project_id, title="Task B", difficulty_points=2)

        dependencies = [
            TaskDependency(blocking_task_id=task_a.id, blocked_task_id=task_b.id),
        ]

        # Original schedule
        original_schedule = calculator.calculate_schedule(
            tasks=[task_a, task_b],
            dependencies=dependencies,
            project_start_date=start_date,
        )

        # Delay task A
        new_end_date = original_schedule.task_schedules[
            task_a.id
        ].expected_end_date + timedelta(days=5)

        new_schedule = calculator.recalculate_from_delay(
            tasks=[task_a, task_b],
            dependencies=dependencies,
            delayed_task_id=task_a.id,
            new_end_date=new_end_date,
        )

        # Task B should now start later
        original_b_start = original_schedule.task_schedules[
            task_b.id
        ].expected_start_date
        new_b_start = new_schedule.task_schedules[task_b.id].expected_start_date
        assert new_b_start > original_b_start

    def test_updates_project_end_date_on_delay(
        self, calculator, project_id, start_date
    ):
        """Project end date should be updated when critical task is delayed."""
        task = Task(project_id=project_id, title="Task", difficulty_points=3)

        original_schedule = calculator.calculate_schedule(
            tasks=[task],
            dependencies=[],
            project_start_date=start_date,
        )

        new_end_date = original_schedule.task_schedules[
            task.id
        ].expected_end_date + timedelta(days=10)

        new_schedule = calculator.recalculate_from_delay(
            tasks=[task],
            dependencies=[],
            delayed_task_id=task.id,
            new_end_date=new_end_date,
        )

        # New project end date should be later
        assert new_schedule.project_end_date >= original_schedule.project_end_date
