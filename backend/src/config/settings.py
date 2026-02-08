"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Environment-driven configuration for adapters and services."""

    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)

    app_env: str = "local"

    email_provider: str = "mock"
    llm_provider: str = "mock"
    token_provider: str = "mock"
    encryption_provider: str = "mock"
    notification_provider: str = "mock"

    global_llm_api_key: str | None = None
    global_llm_base_url: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return cached settings instance."""
    return AppSettings()
