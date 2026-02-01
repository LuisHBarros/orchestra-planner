"""LLM domain errors."""

from backend.src.domain.errors.base import DomainError


class LLMError(DomainError):
    """Base exception for LLM-related errors."""

    pass


class LLMNotConfiguredError(LLMError):
    """Raised when LLM is not enabled for the project (BR-LLM-001)."""

    def __init__(self, project_id: str):
        super().__init__(
            f"LLM is not configured for project: {project_id}",
            status=400,
        )


class LLMProviderError(LLMError):
    """Raised when LLM provider returns an error."""

    def __init__(self, provider: str, detail: str):
        super().__init__(
            f"LLM provider '{provider}' error: {detail}",
            status=502,
        )
        self.provider = provider
        self.detail = detail


class LLMRateLimitError(LLMError):
    """Raised when LLM provider rate limit is exceeded."""

    def __init__(self, provider: str, retry_after: int | None = None):
        msg = f"Rate limit exceeded for provider: {provider}"
        if retry_after:
            msg += f" (retry after {retry_after}s)"
        super().__init__(msg, status=429)
        self.provider = provider
        self.retry_after = retry_after


class LLMInvalidResponseError(LLMError):
    """Raised when LLM response cannot be parsed."""

    def __init__(self, expected: str):
        super().__init__(
            f"Invalid LLM response, expected: {expected}",
            status=502,
        )
        self.expected = expected


class LLMAPIKeyDecryptionError(LLMError):
    """Raised when API key cannot be decrypted (BR-LLM-002)."""

    def __init__(self):
        super().__init__(
            "Failed to decrypt LLM API key",
            status=500,
        )
