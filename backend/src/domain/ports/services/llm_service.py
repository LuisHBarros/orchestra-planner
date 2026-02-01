"""LLM service port (BR-LLM-003)."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class DifficultyEstimation:
    """Result of LLM difficulty estimation."""

    points: int  # Story points (1-13 typically)
    confidence: float  # 0.0 to 1.0
    reasoning: str  # Explanation for the estimate


@dataclass(frozen=True)
class ProgressEstimation:
    """Result of LLM progress estimation."""

    percentage: int  # 0-100
    confidence: float  # 0.0 to 1.0
    reasoning: str  # Explanation for the estimate


class LLMService(Protocol):
    """
    Port for LLM operations.

    BR-LLM-003: LLM can be used to:
    - Estimate Task Difficulty based on description.
    - Calculate % progress based on textual reports.
    """

    async def estimate_difficulty(
        self,
        task_title: str,
        task_description: str,
        project_context: str | None = None,
    ) -> DifficultyEstimation:
        """
        Estimate task difficulty in story points.

        BR-LLM-003: LLM can estimate Task Difficulty based on description.

        Args:
            task_title: The task title.
            task_description: Detailed task description.
            project_context: Optional project context for better estimation.

        Returns:
            DifficultyEstimation with points, confidence, and reasoning.

        Raises:
            LLMProviderError: If LLM provider returns an error.
            LLMRateLimitError: If rate limit is exceeded.
            LLMInvalidResponseError: If response cannot be parsed.
        """
        ...

    async def estimate_progress(
        self,
        task_title: str,
        task_description: str,
        reports: list[str],
    ) -> ProgressEstimation:
        """
        Calculate % progress based on textual reports.

        BR-LLM-003: LLM can calculate % progress based on textual reports.

        Args:
            task_title: The task title.
            task_description: Original task description.
            reports: List of progress reports submitted by the employee.

        Returns:
            ProgressEstimation with percentage, confidence, and reasoning.

        Raises:
            LLMProviderError: If LLM provider returns an error.
            LLMRateLimitError: If rate limit is exceeded.
            LLMInvalidResponseError: If response cannot be parsed.
        """
        ...
