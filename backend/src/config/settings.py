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
    database_url: str | None = None
    db_echo: bool = False

    email_provider: str = "mock"
    llm_provider: str = "mock"
    token_provider: str = "mock"
    encryption_provider: str = "mock"
    notification_provider: str = "mock"
    rate_limit_provider: str = "memory"

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
    redis_url: str | None = None

    cors_allow_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    cors_allow_methods: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    cors_allow_headers: list[str] = ["*"]
    cors_allow_credentials: bool = True

    auth_magic_link_limit: int = 5
    auth_magic_link_window_seconds: int = 300
    auth_verify_limit: int = 20
    auth_verify_window_seconds: int = 300
    auth_refresh_limit: int = 30
    auth_refresh_window_seconds: int = 300
    auth_revoke_limit: int = 30
    auth_revoke_window_seconds: int = 300


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return cached settings instance."""
    return AppSettings()
