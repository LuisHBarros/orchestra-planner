"""Task entity definition."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from backend.src.domain.time import utcnow


class TaskStatus(str, Enum):
    """
    Task status values as defined in BR-TASK-003.

    Valid transitions:
    - Todo → Doing, Blocked, Cancelled
    - Doing → Done, Blocked, Todo (abandonment)
    - Blocked → Todo (unblocked)
    """

    TODO = "Todo"
    DOING = "Doing"
    BLOCKED = "Blocked"
    DONE = "Done"
    CANCELLED = "Cancelled"


# Valid status transitions as per BR-TASK-003
VALID_STATUS_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.TODO: {TaskStatus.DOING, TaskStatus.BLOCKED, TaskStatus.CANCELLED},
    TaskStatus.DOING: {TaskStatus.DONE, TaskStatus.BLOCKED, TaskStatus.TODO},
    TaskStatus.BLOCKED: {TaskStatus.TODO},
    TaskStatus.DONE: set(),  # Terminal state
    TaskStatus.CANCELLED: set(),  # Terminal state
}


@dataclass
class Task:
    """
    A unit of work with a difficulty score and status.

    BR-TASK-001: Only the Manager can create, edit, or delete Tasks.
    BR-TASK-002: A Task must have a numeric Difficulty (Story Points).
    BR-TASK-003: Task Status Transitions are strict.
    BR-TASK-004: A Task cannot be selected (Doing) if Difficulty is not set.
    """

    project_id: UUID
    title: str
    id: UUID = field(default_factory=uuid4)
    description: str = field(default="")
    difficulty_points: int | None = field(default=None)
    status: TaskStatus = field(default=TaskStatus.TODO)
    assignee_id: UUID | None = field(default=None)  # References ProjectMember
    required_role_id: UUID | None = field(default=None)
    progress_percent: int = field(default=0)
    expected_start_date: datetime | None = field(default=None)
    expected_end_date: datetime | None = field(default=None)
    actual_end_date: datetime | None = field(default=None)
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        """Validate task attributes."""
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")
        self.title = self.title.strip()
        if self.description:
            self.description = self.description.strip()
        if self.progress_percent < 0 or self.progress_percent > 100:
            raise ValueError("Progress percent must be between 0 and 100")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Task):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = utcnow()

    def can_transition_to(self, new_status: TaskStatus) -> bool:
        """Check if transition to new status is valid per BR-TASK-003."""
        return new_status in VALID_STATUS_TRANSITIONS.get(self.status, set())

    def transition_to(self, new_status: TaskStatus) -> None:
        """
        Transition task to a new status.

        Raises:
            ValueError: If transition is not valid.
        """
        if not self.can_transition_to(new_status):
            raise ValueError(
                f"Invalid status transition from {self.status.value} to {new_status.value}"
            )
        self.status = new_status
        self._update_timestamp()

        if new_status == TaskStatus.DONE:
            self.actual_end_date = utcnow()
            self.progress_percent = 100

    def can_be_selected(self) -> bool:
        """
        Check if task can be selected for work.

        BR-TASK-004: Task cannot be selected if Difficulty is not set.
        """
        return self.status == TaskStatus.TODO and self.difficulty_points is not None

    def select(self, assignee_id: UUID) -> None:
        """
        Select the task for work (assign to an employee).

        BR-TASK-004: Cannot select if difficulty is not set.
        """
        if not self.can_be_selected():
            if self.difficulty_points is None:
                raise ValueError("Cannot select task without difficulty points set")
            raise ValueError(f"Cannot select task with status {self.status.value}")

        self.transition_to(TaskStatus.DOING)
        self.assignee_id = assignee_id

    def abandon(self) -> None:
        """
        Abandon the task (BR-ABANDON).

        The task returns to Todo status and is unassigned.
        """
        if self.status != TaskStatus.DOING:
            raise ValueError("Can only abandon tasks that are in progress")

        self.transition_to(TaskStatus.TODO)
        self.assignee_id = None

    def complete(self) -> None:
        """Complete the task."""
        if self.status != TaskStatus.DOING:
            raise ValueError("Can only complete tasks that are in progress")
        self.transition_to(TaskStatus.DONE)

    def block(self) -> None:
        """Block the task (due to dependency issues)."""
        if self.status not in (TaskStatus.TODO, TaskStatus.DOING):
            raise ValueError(f"Cannot block task with status {self.status.value}")
        self.transition_to(TaskStatus.BLOCKED)

    def unblock(self) -> None:
        """Unblock the task."""
        if self.status != TaskStatus.BLOCKED:
            raise ValueError("Task is not blocked")
        self.transition_to(TaskStatus.TODO)

    def cancel(self) -> None:
        """Cancel the task (Manager decision)."""
        if self.status != TaskStatus.TODO:
            raise ValueError("Can only cancel tasks in Todo status")
        self.transition_to(TaskStatus.CANCELLED)

    def set_difficulty(self, points: int) -> None:
        """Set the difficulty points for the task."""
        if points < 0:
            raise ValueError("Difficulty points cannot be negative")
        self.difficulty_points = points
        self._update_timestamp()

    def update_progress(self, percent: int) -> None:
        """Update task progress (0-100)."""
        if percent < 0 or percent > 100:
            raise ValueError("Progress must be between 0 and 100")
        self.progress_percent = percent
        self._update_timestamp()

    def update_schedule(
        self,
        expected_start_date: datetime | None = None,
        expected_end_date: datetime | None = None,
    ) -> None:
        """
        Update task schedule dates.

        BR-SCHED-005: If task has started, only End Date can change.

        Raises:
            ScheduleUpdateError: If trying to change start date of in-progress task.
        """
        from backend.src.domain.errors import ScheduleUpdateError

        if self.status == TaskStatus.DOING and expected_start_date is not None:
            # BR-SCHED-005: Cannot change start date of in-progress task
            raise ScheduleUpdateError(
                str(self.id),
                "cannot change start date of in-progress task",
            )

        if expected_start_date is not None:
            self.expected_start_date = expected_start_date

        if expected_end_date is not None:
            self.expected_end_date = expected_end_date

        self._update_timestamp()

    @property
    def is_delayed(self) -> bool:
        """Check if task is delayed (BR-SCHED-001)."""
        if self.expected_end_date is None:
            return False
        if self.status == TaskStatus.DONE:
            return False
        return utcnow() > self.expected_end_date
