"""Tests for EmailNotificationService."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from backend.src.adapters.services.email_notification_service import EmailNotificationService
from backend.src.domain.ports.services import DailyReportData, WorkloadAlertData


@pytest.fixture
def email_service():
    mock = AsyncMock()
    mock.send_email = AsyncMock()
    return mock


@pytest.mark.asyncio
async def test_send_daily_report(email_service):
    service = EmailNotificationService(email_service)
    report = DailyReportData(
        project_id=uuid4(),
        project_name="Project",
        total_tasks=10,
        completed_today=2,
        blocked_tasks=1,
        delayed_tasks=0,
        team_workload_summary={"Alice": "Healthy"},
    )

    await service.send_daily_report("manager@example.com", report)

    email_service.send_email.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_workload_alert(email_service):
    service = EmailNotificationService(email_service)
    alert = WorkloadAlertData(
        project_id=uuid4(),
        project_name="Project",
        employee_id=uuid4(),
        employee_name="Bob",
        employee_email="bob@example.com",
        current_workload_ratio=1.7,
    )

    await service.send_workload_alert("manager@example.com", alert)

    email_service.send_email.assert_awaited_once()
