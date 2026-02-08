"""Application settings loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Environment-driven configuration for adapters and services."""

    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)

    app_env: str = "local"

    public_base_url: str = "http://localhost:8000"
    log_level: str = "INFO"

    email_provider: str = "mock"
    llm_provider: str = "mock"
    token_provider: str = "mock"
    encryption_provider: str = "mock"
    notification_provider: str = "mock"

    global_llm_api_key: str | None = None
    global_llm_base_url: str | None = None
    llm_model: str | None = None

    jwt_secret_key: str | None = None
    jwt_algorithm: str = "HS256"
    access_token_expiry_minutes: int = 30
    refresh_token_expiry_minutes: int = 10080

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    smtp_use_tls: bool = True

    encryption_key: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return cached settings instance."""
    return AppSettings()
