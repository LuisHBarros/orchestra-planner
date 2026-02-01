"""Notification service port (BR-NOTIF)."""

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class DailyReportData:
    """
    Data for manager daily report.

    BR-NOTIF-001: Managers receive a Daily Report summarizing
    progress and blockers.
    """

    project_id: UUID
    project_name: str
    total_tasks: int
    completed_today: int
    blocked_tasks: int
    delayed_tasks: int
    team_workload_summary: dict[str, str]  # member_name -> workload_status


@dataclass(frozen=True)
class WorkloadAlertData:
    """
    Data for workload impossible alert.

    BR-NOTIF-002: Alerts are sent to Managers if an Employee's
    workload becomes Impossible.
    """

    project_id: UUID
    project_name: str
    employee_id: UUID
    employee_name: str
    employee_email: str
    current_workload_ratio: float


@dataclass(frozen=True)
class NewTaskToastData:
    """
    Data for new task notification.

    BR-NOTIF-003: "Toasts" are sent to Employees when a task
    matching their role is added.
    """

    project_id: UUID
    project_name: str
    task_id: UUID
    task_title: str
    required_role: str | None


class NotificationService(Protocol):
    """
    Port for notification operations.

    Handles all notification types defined in BR-NOTIF rules.
    """

    async def send_daily_report(
        self,
        manager_email: str,
        report: DailyReportData,
    ) -> None:
        """
        Send daily progress report to manager.

        BR-NOTIF-001: Managers receive a Daily Report summarizing
        progress and blockers.

        Args:
            manager_email: The manager's email address.
            report: Daily report data.

        Raises:
            EmailDeliveryError: If email cannot be sent.
            InvalidRecipientError: If email is invalid.
        """
        ...

    async def send_workload_alert(
        self,
        manager_email: str,
        alert: WorkloadAlertData,
    ) -> None:
        """
        Alert manager when employee workload becomes Impossible.

        BR-NOTIF-002: Alerts are sent to Managers if an Employee's
        workload becomes Impossible.

        Args:
            manager_email: The manager's email address.
            alert: Workload alert data.

        Raises:
            EmailDeliveryError: If email cannot be sent.
            InvalidRecipientError: If email is invalid.
        """
        ...

    async def send_new_task_toast(
        self,
        employee_ids: list[UUID],
        toast: NewTaskToastData,
    ) -> None:
        """
        Send in-app notification to employees about new task.

        BR-NOTIF-003: "Toasts" are sent to Employees when a task
        matching their role is added.

        Args:
            employee_ids: List of employee IDs to notify.
            toast: New task notification data.

        Raises:
            NotificationDeliveryError: If notification cannot be delivered.
        """
        ...

    async def send_deadline_warning(
        self,
        employee_email: str,
        task_id: UUID,
        task_title: str,
        hours_remaining: int,
    ) -> None:
        """
        Send deadline warning to assignee.

        UC-084: Send Deadline Warning when task is 24h from deadline
        and not Done.

        Args:
            employee_email: The assignee's email address.
            task_id: The task ID.
            task_title: The task title.
            hours_remaining: Hours until deadline.

        Raises:
            EmailDeliveryError: If email cannot be sent.
            InvalidRecipientError: If email is invalid.
        """
        ...

    async def send_employee_daily_summary(
        self,
        employee_email: str,
        employee_name: str,
        assigned_tasks: list[dict],
    ) -> None:
        """
        Send daily summary to employee.

        UC-083: Send Employee Daily Email with summary of assigned
        tasks and deadlines.

        Args:
            employee_email: The employee's email address.
            employee_name: The employee's name.
            assigned_tasks: List of assigned tasks with deadlines.

        Raises:
            EmailDeliveryError: If email cannot be sent.
            InvalidRecipientError: If email is invalid.
        """
        ...
