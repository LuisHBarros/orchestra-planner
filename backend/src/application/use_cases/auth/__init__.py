"""Authentication use cases."""

from backend.src.application.use_cases.auth.request_magic_link import (
    RequestMagicLinkUseCase,
)

from backend.src.application.use_cases.auth.verify_magic_link import (
    VerifyMagicLinkUseCase,
)

__all__ = ["RequestMagicLinkUseCase", "VerifyMagicLinkUseCase"]
