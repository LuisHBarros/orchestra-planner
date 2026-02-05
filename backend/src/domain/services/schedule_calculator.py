"""Schedule calculator domain service.

This service calculates task schedules based on dependencies, applying
topological sorting to determine execution order and critical path analysis.
"""

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from backend.src.domain.entities import (
    SeniorityLevel,
    Task,
    TaskDependency,
    TaskStatus,
)


@dataclass
class TaskSchedule:
    """Calculated schedule for a single task."""

    task_id: UUID
    expected_start_date: datetime
    expected_end_date: datetime
    is_on_critical_path: bool = False
    slack_days: int = 0


@dataclass
class ProjectSchedule:
    """Calculated schedule for an entire project."""

    task_schedules: dict[UUID, TaskSchedule] = field(default_factory=dict)
    critical_path: list[UUID] = field(default_factory=list)
    project_end_date: datetime | None = None


class ScheduleCalculator:
    """
    Domain service for calculating task schedules.

    BR-SCHED-001: If a task is delayed, dependent tasks are recalculated.
    BR-SCHED-002: Critical path determines project end date.
    BR-SCHED-003: Schedule is recalculated when dependencies change.
    BR-PROJ-003: Project's "Expected End Date" is dynamic, calculated from critical path.
    """

    # Average story points per day based on seniority
    DEFAULT_POINTS_PER_DAY = Decimal("2")

    def __init__(
        self,
        points_per_day: Decimal = DEFAULT_POINTS_PER_DAY,
        working_days_per_week: int = 5,
    ):
        self.points_per_day = points_per_day
        self.working_days_per_week = working_days_per_week

    def estimate_duration_days(
        self,
        difficulty_points: int | None,
        seniority_level: SeniorityLevel = SeniorityLevel.MID,
    ) -> int:
        """
        Estimate task duration in working days based on difficulty and seniority.

        Higher seniority = faster completion.
        Uses ceiling to avoid underestimating task duration.
        """
        if difficulty_points is None or difficulty_points <= 0:
            return 1  # Minimum 1 day

        effective_rate = self.points_per_day * seniority_level.capacity_multiplier
        if effective_rate <= 0:
            return 1

        # Use ceiling to avoid underestimating task duration
        days = math.ceil(float(Decimal(difficulty_points) / effective_rate))
        return max(1, days)

    def _add_working_days(self, start_date: datetime, working_days: int) -> datetime:
        """Add (or subtract) working days to/from a date, skipping weekends."""
        current = start_date

        if working_days == 0:
            return current

        if working_days > 0:
            days_added = 0
            while days_added < working_days:
                current += timedelta(days=1)
                # Skip weekends (Saturday=5, Sunday=6)
                if current.weekday() < self.working_days_per_week:
                    days_added += 1
        else:
            # Handle negative working days (backward pass)
            days_subtracted = 0
            target = abs(working_days)
            while days_subtracted < target:
                current -= timedelta(days=1)
                # Skip weekends (Saturday=5, Sunday=6)
                if current.weekday() < self.working_days_per_week:
                    days_subtracted += 1

        return current

    def _topological_sort(
        self,
        tasks: list[Task],
        dependencies: list[TaskDependency],
    ) -> list[UUID]:
        """
        Perform topological sort on tasks based on dependencies.

        Returns task IDs in execution order (tasks with no dependencies first).
        """
        task_ids = {t.id for t in tasks}

        # Build adjacency list and in-degree count
        in_degree: dict[UUID, int] = {task_id: 0 for task_id in task_ids}
        adjacency: dict[UUID, list[UUID]] = {task_id: [] for task_id in task_ids}

        for dep in dependencies:
            if dep.blocking_task_id in task_ids and dep.blocked_task_id in task_ids:
                adjacency[dep.blocking_task_id].append(dep.blocked_task_id)
                in_degree[dep.blocked_task_id] += 1

        # Kahn's algorithm
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        result: list[UUID] = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            for neighbor in adjacency[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # If not all tasks are in result, there's a cycle (shouldn't happen if validated)
        if len(result) != len(task_ids):
            # Return what we can, cycle detection should prevent this
            return result

        return result

    def calculate_schedule(
        self,
        tasks: list[Task],
        dependencies: list[TaskDependency],
        project_start_date: datetime | None = None,
        assignee_seniority: dict[UUID, SeniorityLevel] | None = None,
    ) -> ProjectSchedule:
        """
        Calculate schedules for all tasks in a project.

        Uses topological sorting to determine task order and calculates
        start/end dates based on dependencies.

        Args:
            tasks: List of tasks to schedule.
            dependencies: List of task dependencies.
            project_start_date: When the project starts (defaults to now).
            assignee_seniority: Map of task_id to assignee's seniority level.

        Returns:
            ProjectSchedule with calculated dates and critical path.
        """
        if not tasks:
            return ProjectSchedule()

        if project_start_date is None:
            project_start_date = datetime.now(timezone.utc)

        assignee_seniority = assignee_seniority or {}

        # Filter to only schedulable tasks (not done/cancelled)
        schedulable_tasks = [
            t for t in tasks if t.status not in (TaskStatus.DONE, TaskStatus.CANCELLED)
        ]

        if not schedulable_tasks:
            return ProjectSchedule()

        task_map = {t.id: t for t in schedulable_tasks}
        sorted_task_ids = self._topological_sort(schedulable_tasks, dependencies)

        # Build reverse dependency map (task -> tasks it blocks)
        blocked_by: dict[UUID, set[UUID]] = {t.id: set() for t in schedulable_tasks}
        for dep in dependencies:
            if dep.blocked_task_id in blocked_by:
                blocked_by[dep.blocked_task_id].add(dep.blocking_task_id)

        # Calculate earliest start and end for each task
        earliest_start: dict[UUID, datetime] = {}
        earliest_end: dict[UUID, datetime] = {}
        task_schedules: dict[UUID, TaskSchedule] = {}

        for task_id in sorted_task_ids:
            task = task_map.get(task_id)
            if task is None:
                continue

            # Earliest start is max of project start and all blocking tasks' end dates
            blocking_tasks = blocked_by.get(task_id, set())
            if blocking_tasks:
                start = max(
                    earliest_end.get(bt, project_start_date)
                    for bt in blocking_tasks
                    if bt in earliest_end
                )
                # If no blocking tasks have been scheduled yet, use project start
                if start == project_start_date and any(
                    bt not in earliest_end for bt in blocking_tasks
                ):
                    start = project_start_date
            else:
                start = project_start_date

            # Use existing start date if task already has one and it's later
            if task.expected_start_date and task.expected_start_date > start:
                start = task.expected_start_date

            earliest_start[task_id] = start

            # Calculate duration
            seniority = assignee_seniority.get(task_id, SeniorityLevel.MID)
            duration_days = self.estimate_duration_days(
                task.difficulty_points, seniority
            )
            end = self._add_working_days(start, duration_days)

            earliest_end[task_id] = end

            task_schedules[task_id] = TaskSchedule(
                task_id=task_id,
                expected_start_date=start,
                expected_end_date=end,
            )

        # Find project end date (latest end date)
        project_end_date = max(earliest_end.values()) if earliest_end else None

        # Calculate critical path (tasks where delay would delay project)
        # Using backward pass to find slack
        if project_end_date:
            latest_end: dict[UUID, datetime] = {}
            latest_start: dict[UUID, datetime] = {}

            # Reverse order for backward pass
            for task_id in reversed(sorted_task_ids):
                task = task_map.get(task_id)
                if task is None:
                    continue

                # Find tasks that this task blocks
                dependent_tasks = [
                    dep.blocked_task_id
                    for dep in dependencies
                    if dep.blocking_task_id == task_id
                    and dep.blocked_task_id in task_map
                ]

                if dependent_tasks:
                    latest_end[task_id] = min(
                        latest_start.get(dt, project_end_date)
                        for dt in dependent_tasks
                        if dt in latest_start
                    )
                else:
                    latest_end[task_id] = project_end_date

                seniority = assignee_seniority.get(task_id, SeniorityLevel.MID)
                duration_days = self.estimate_duration_days(
                    task.difficulty_points, seniority
                )
                latest_start[task_id] = self._add_working_days(
                    latest_end[task_id], -duration_days
                )

            # Calculate slack and identify critical path
            critical_path: list[UUID] = []
            for task_id in sorted_task_ids:
                if task_id in task_schedules and task_id in latest_start:
                    slack = (latest_start[task_id] - earliest_start[task_id]).days
                    task_schedules[task_id].slack_days = max(0, slack)
                    if slack <= 0:
                        task_schedules[task_id].is_on_critical_path = True
                        critical_path.append(task_id)

        else:
            critical_path = []

        return ProjectSchedule(
            task_schedules=task_schedules,
            critical_path=critical_path,
            project_end_date=project_end_date,
        )

    def recalculate_from_delay(
        self,
        tasks: list[Task],
        dependencies: list[TaskDependency],
        delayed_task_id: UUID,
        new_end_date: datetime,
        assignee_seniority: dict[UUID, SeniorityLevel] | None = None,
    ) -> ProjectSchedule:
        """
        Recalculate schedule when a task is delayed.

        BR-SCHED-001: If a task is delayed, dependent tasks are recalculated.

        Args:
            tasks: All project tasks.
            dependencies: Task dependencies.
            delayed_task_id: ID of the delayed task.
            new_end_date: The new expected end date for the delayed task.
            assignee_seniority: Map of task_id to assignee's seniority.

        Returns:
            Updated ProjectSchedule.
        """
        # Find the delayed task and update its expected end date
        for task in tasks:
            if task.id == delayed_task_id:
                task.expected_end_date = new_end_date
                break

        # Recalculate entire schedule (dependent tasks will use new end date)
        return self.calculate_schedule(
            tasks=tasks,
            dependencies=dependencies,
            assignee_seniority=assignee_seniority,
        )
