"""Basic service implementations for local development and tests."""

from __future__ import annotations

import base64
import hashlib
import secrets
from dataclasses import dataclass, field
from typing import Any, Dict
from uuid import UUID

from backend.src.domain.ports.services import (
    DifficultyEstimation,
    EmailMessage,
    ProgressEstimation,
    TokenPair,
)


@dataclass
class MockEmailService:
    """In-memory email service for local development."""

    sent_messages: list[EmailMessage] = field(default_factory=list)

    async def send_email(self, message: EmailMessage) -> None:
        self.sent_messages.append(message)


class InMemoryTokenService:
    """Basic token service backed by in-memory storage."""

    def __init__(self) -> None:
        self._access_tokens: dict[str, dict[str, Any]] = {}
        self._refresh_tokens: dict[str, dict[str, Any]] = {}

    async def generate_tokens(
        self, user_id: UUID, claims: Dict[str, Any] | None = None
    ) -> TokenPair:
        payload = {"user_id": str(user_id), **(claims or {})}
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(48)
        self._access_tokens[access_token] = payload
        self._refresh_tokens[refresh_token] = payload
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def verify_token(self, token: str) -> Dict[str, Any] | None:
        return self._access_tokens.get(token)

    async def refresh_token(self, token: str) -> Dict[str, Any] | None:
        payload = self._refresh_tokens.get(token)
        if not payload:
            return None
        access_token = secrets.token_urlsafe(32)
        self._access_tokens[access_token] = payload
        return {"access_token": access_token, **payload}

    async def revoke_token(self, token: str) -> Dict[str, Any] | None:
        payload = self._access_tokens.pop(token, None)
        if payload:
            return payload
        return self._refresh_tokens.pop(token, None)


class SimpleEncryptionService:
    """Basic reversible encryption for development only."""

    def __init__(self, secret: str = "dev-secret") -> None:
        self._secret = secret

    async def encrypt(self, plaintext: str) -> str:
        key = hashlib.sha256(self._secret.encode()).digest()
        data = plaintext.encode()
        xored = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
        return base64.urlsafe_b64encode(xored).decode()

    async def decrypt(self, ciphertext: str) -> str:
        key = hashlib.sha256(self._secret.encode()).digest()
        raw = base64.urlsafe_b64decode(ciphertext.encode())
        decoded = bytes(b ^ key[i % len(key)] for i, b in enumerate(raw))
        return decoded.decode()


class MockLLMService:
    """Deterministic mock for LLM estimations."""

    async def estimate_difficulty(
        self,
        task_title: str,
        task_description: str,
        project_context: str | None = None,
    ) -> DifficultyEstimation:
        text = f"{task_title} {task_description} {project_context or ''}".strip()
        length = max(1, len(text.split()))
        points = min(13, max(1, length // 10))
        return DifficultyEstimation(
            points=points,
            confidence=0.3,
            reasoning="Mock estimate based on text length.",
        )

    async def estimate_progress(
        self,
        task_title: str,
        task_description: str,
        reports: list[str],
    ) -> ProgressEstimation:
        total_words = sum(len(r.split()) for r in reports)
        percentage = min(100, max(0, total_words))
        return ProgressEstimation(
            percentage=percentage,
            confidence=0.2,
            reasoning="Mock estimate based on report size.",
        )


class MockNotificationService:
    """No-op notification service for local development."""

    async def send_daily_report(self, manager_email: str, report) -> None:
        return None

    async def send_workload_alert(self, manager_email: str, alert) -> None:
        return None

    async def send_new_task_toast(self, employee_ids: list[UUID], toast) -> None:
        return None

    async def send_deadline_warning(
        self, employee_email: str, task_id: UUID, task_title: str, hours_remaining: int
    ) -> None:
        return None

    async def send_employee_daily_summary(
        self, employee_email: str, employee_name: str, assigned_tasks: list[dict]
    ) -> None:
        return None
