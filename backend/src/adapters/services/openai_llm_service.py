"""OpenAI-backed LLM service implementation."""

from __future__ import annotations

import json

from backend.src.config.settings import AppSettings
from backend.src.domain.errors import (
    LLMInvalidResponseError,
    LLMProviderError,
    LLMRateLimitError,
)
from backend.src.domain.ports.services import DifficultyEstimation, ProgressEstimation


class OpenAILLMService:
    """LLM service using OpenAI chat completions."""

    def __init__(self, settings: AppSettings) -> None:
        if not settings.global_llm_api_key:
            raise RuntimeError("GLOBAL_LLM_API_KEY is required when LLM_PROVIDER != mock")

        self._api_key = settings.global_llm_api_key
        self._model = settings.llm_model or "gpt-4o-mini"
        self._base_url = settings.global_llm_base_url

    def _client(self):
        from openai import OpenAI

        if self._base_url:
            return OpenAI(api_key=self._api_key, base_url=self._base_url)
        return OpenAI(api_key=self._api_key)

    async def estimate_difficulty(
        self,
        task_title: str,
        task_description: str,
        project_context: str | None = None,
    ) -> DifficultyEstimation:
        prompt = {
            "task_title": task_title,
            "task_description": task_description,
            "project_context": project_context,
            "output": {
                "points": "int",
                "confidence": "float(0..1)",
                "reasoning": "str",
            },
        }
        data = await self._complete_json(prompt)
        try:
            return DifficultyEstimation(
                points=int(data["points"]),
                confidence=float(data["confidence"]),
                reasoning=str(data["reasoning"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise LLMInvalidResponseError("difficulty estimation json") from exc

    async def estimate_progress(
        self,
        task_title: str,
        task_description: str,
        reports: list[str],
    ) -> ProgressEstimation:
        prompt = {
            "task_title": task_title,
            "task_description": task_description,
            "reports": reports,
            "output": {
                "percentage": "int(0..100)",
                "confidence": "float(0..1)",
                "reasoning": "str",
            },
        }
        data = await self._complete_json(prompt)
        try:
            return ProgressEstimation(
                percentage=int(data["percentage"]),
                confidence=float(data["confidence"]),
                reasoning=str(data["reasoning"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise LLMInvalidResponseError("progress estimation json") from exc

    async def _complete_json(self, payload: dict) -> dict:
        try:
            response = self._client().chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "system",
                        "content": "Return strict JSON only.",
                    },
                    {
                        "role": "user",
                        "content": json.dumps(payload),
                    },
                ],
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            error_type = exc.__class__.__name__.lower()
            if "rate" in error_type or "429" in str(exc):
                raise LLMRateLimitError("openai") from exc
            raise LLMProviderError("openai", str(exc)) from exc

        try:
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
        except Exception as exc:
            raise LLMInvalidResponseError("json_object") from exc
