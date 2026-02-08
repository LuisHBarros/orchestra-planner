"""Email-backed notification service implementation."""

from __future__ import annotations

from uuid import UUID

from backend.src.domain.ports.services import (
    DailyReportData,
    EmailMessage,
    EmailService,
    NewTaskToastData,
    WorkloadAlertData,
)


class EmailNotificationService:
    """Notification adapter that renders notifications as emails."""

    def __init__(self, email_service: EmailService) -> None:
        self._email_service = email_service

    async def send_daily_report(
        self,
        manager_email: str,
        report: DailyReportData,
    ) -> None:
        lines = [
            f"Project: {report.project_name}",
            f"Total tasks: {report.total_tasks}",
            f"Completed today: {report.completed_today}",
            f"Blocked: {report.blocked_tasks}",
            f"Delayed: {report.delayed_tasks}",
        ]
        if report.team_workload_summary:
            lines.append("Workload summary:")
            lines.extend(
                f"- {name}: {state}"
                for name, state in report.team_workload_summary.items()
            )

        await self._email_service.send_email(
            EmailMessage(
                recipients=[manager_email],
                subject=f"Daily report: {report.project_name}",
                body_text="\n".join(lines),
            )
        )

    async def send_workload_alert(
        self,
        manager_email: str,
        alert: WorkloadAlertData,
    ) -> None:
        await self._email_service.send_email(
            EmailMessage(
                recipients=[manager_email],
                subject=f"Workload alert: {alert.project_name}",
                body_text=(
                    f"{alert.employee_name} is in impossible workload state "
                    f"({alert.current_workload_ratio:.2f})."
                ),
            )
        )

    async def send_new_task_toast(
        self,
        employee_ids: list[UUID],
        toast: NewTaskToastData,
    ) -> None:
        # No employee email directory is available in this adapter.
        return None

    async def send_deadline_warning(
        self,
        employee_email: str,
        task_id,
        task_title: str,
        hours_remaining: int,
    ) -> None:
        await self._email_service.send_email(
            EmailMessage(
                recipients=[employee_email],
                subject="Task deadline warning",
                body_text=(
                    f"Task '{task_title}' is due in {hours_remaining}h "
                    f"(task_id={task_id})."
                ),
            )
        )

    async def send_employee_daily_summary(
        self,
        employee_email: str,
        employee_name: str,
        assigned_tasks: list[dict],
    ) -> None:
        lines = [f"Hello {employee_name}, here's your daily summary:"]
        for task in assigned_tasks:
            title = task.get("title", "Untitled")
            deadline = task.get("deadline", "N/A")
            lines.append(f"- {title} (deadline: {deadline})")

        await self._email_service.send_email(
            EmailMessage(
                recipients=[employee_email],
                subject="Daily task summary",
                body_text="\n".join(lines),
            )
        )
