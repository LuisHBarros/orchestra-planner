"""TaskLog entity definition for audit and history tracking."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4


class TaskLogType(str, Enum):
    """Types of task log entries for audit trail."""

    ASSIGN = "ASSIGN"
    UNASSIGN = "UNASSIGN"
    REPORT = "REPORT"
    ABANDON = "ABANDON"
    STATUS_CHANGE = "STATUS_CHANGE"


@dataclass
class TaskLog:
    """
    Audit log entry for task history.

    Handles:
    - BR-ASSIGN-005: All assignments and un-assignments are logged.
    - UC-042: Task reports are saved for progress tracking.
    - BR-ABANDON-002: Reason for abandonment is recorded.
    """

    task_id: UUID
    author_id: UUID  # ProjectMember ID
    log_type: TaskLogType
    id: UUID = field(default_factory=uuid4)
    content: str = field(default="")  # Reason for abandon or report text
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Validate log entry."""
        if self.log_type == TaskLogType.ABANDON and not self.content.strip():
            raise ValueError("Abandonment reason is required (BR-ABANDON-002)")
        if self.content:
            self.content = self.content.strip()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TaskLog):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def create_assignment_log(
        cls,
        task_id: UUID,
        author_id: UUID,
        content: str = "",
    ) -> "TaskLog":
        """Create a log entry for task assignment."""
        return cls(
            task_id=task_id,
            author_id=author_id,
            log_type=TaskLogType.ASSIGN,
            content=content,
        )

    @classmethod
    def create_unassignment_log(
        cls,
        task_id: UUID,
        author_id: UUID,
        content: str = "",
    ) -> "TaskLog":
        """Create a log entry for task unassignment."""
        return cls(
            task_id=task_id,
            author_id=author_id,
            log_type=TaskLogType.UNASSIGN,
            content=content,
        )

    @classmethod
    def create_report_log(
        cls,
        task_id: UUID,
        author_id: UUID,
        report_text: str,
    ) -> "TaskLog":
        """Create a log entry for a task progress report (UC-042)."""
        return cls(
            task_id=task_id,
            author_id=author_id,
            log_type=TaskLogType.REPORT,
            content=report_text,
        )

    @classmethod
    def create_abandon_log(
        cls,
        task_id: UUID,
        author_id: UUID,
        reason: str,
    ) -> "TaskLog":
        """
        Create a log entry for task abandonment.

        BR-ABANDON-002: The user must provide a reason for abandonment.
        """
        if not reason or not reason.strip():
            raise ValueError("Abandonment reason is required")
        return cls(
            task_id=task_id,
            author_id=author_id,
            log_type=TaskLogType.ABANDON,
            content=reason,
        )

    @classmethod
    def create_status_change_log(
        cls,
        task_id: UUID,
        author_id: UUID,
        old_status: str,
        new_status: str,
    ) -> "TaskLog":
        """Create a log entry for a status change."""
        return cls(
            task_id=task_id,
            author_id=author_id,
            log_type=TaskLogType.STATUS_CHANGE,
            content=f"Status changed from {old_status} to {new_status}",
        )
