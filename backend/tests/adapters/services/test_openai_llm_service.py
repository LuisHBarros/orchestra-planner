"""Tests for OpenAILLMService."""

from types import SimpleNamespace

import pytest

from backend.src.adapters.services.openai_llm_service import OpenAILLMService
from backend.src.config.settings import AppSettings


@pytest.fixture
def settings():
    return AppSettings(global_llm_api_key="key", llm_model="gpt-test")


@pytest.mark.asyncio
async def test_estimate_difficulty_parses_json(monkeypatch, settings):
    service = OpenAILLMService(settings)

    fake_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content='{"points":3,"confidence":0.9,"reasoning":"ok"}'
                )
            )
        ]
    )

    async def fake_create(**kwargs):
        return fake_response

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=fake_create))
    )
    monkeypatch.setattr(service, "_client", lambda: fake_client)

    result = await service.estimate_difficulty("title", "desc")

    assert result.points == 3
    assert result.confidence == 0.9


@pytest.mark.asyncio
async def test_estimate_progress_parses_json(monkeypatch, settings):
    service = OpenAILLMService(settings)

    fake_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content='{"percentage":55,"confidence":0.7,"reasoning":"ok"}'
                )
            )
        ]
    )

    async def fake_create(**kwargs):
        return fake_response

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=fake_create))
    )
    monkeypatch.setattr(service, "_client", lambda: fake_client)

    result = await service.estimate_progress("title", "desc", ["r1"])

    assert result.percentage == 55
    assert result.confidence == 0.7
