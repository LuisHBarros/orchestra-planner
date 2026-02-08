"""Tests for SMTPEmailService."""

import pytest

from backend.src.adapters.services.smtp_email_service import SMTPEmailService
from backend.src.config.settings import AppSettings
from backend.src.domain.ports.services import EmailMessage


aiosmtplib = pytest.importorskip("aiosmtplib")


@pytest.fixture
def settings():
    return AppSettings(
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_user="user",
        smtp_password="pass",
        smtp_from_email="noreply@example.com",
        smtp_use_tls=True,
    )


@pytest.mark.asyncio
async def test_send_email_calls_aiosmtplib(monkeypatch, settings):
    service = SMTPEmailService(settings)
    called = {}

    async def fake_send(message, **kwargs):
        called["message"] = message
        called["kwargs"] = kwargs

    monkeypatch.setattr(aiosmtplib, "send", fake_send)

    await service.send_email(
        EmailMessage(
            recipients=["to@example.com"],
            subject="Hello",
            body_text="Text body",
            body_html="<p>HTML</p>",
        )
    )

    assert called["kwargs"]["hostname"] == "smtp.example.com"
    assert called["kwargs"]["username"] == "user"
    assert "to@example.com" in called["kwargs"]["recipients"]
