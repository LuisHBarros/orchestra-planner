"""Tests for JWTTokenService."""

from uuid import uuid4

import pytest

from backend.src.adapters.services.jwt_token_service import JWTTokenService
from backend.src.config.settings import AppSettings


pytest.importorskip("jwt")


@pytest.fixture
def settings():
    return AppSettings(
        jwt_secret_key="secret",
        jwt_algorithm="HS256",
        access_token_expiry_minutes=30,
        refresh_token_expiry_minutes=60,
    )


@pytest.mark.asyncio
async def test_generate_and_verify_access_token(settings):
    service = JWTTokenService(settings)
    user_id = uuid4()

    pair = await service.generate_tokens(user_id)
    payload = await service.verify_token(pair.access_token)

    assert payload is not None
    assert payload["user_id"] == str(user_id)


@pytest.mark.asyncio
async def test_refresh_rotates_tokens(settings):
    service = JWTTokenService(settings)
    pair = await service.generate_tokens(uuid4())

    refreshed = await service.refresh_token(pair.refresh_token)

    assert refreshed is not None
    assert refreshed.access_token != pair.access_token
    assert refreshed.refresh_token != pair.refresh_token


@pytest.mark.asyncio
async def test_revoke_invalidates_token(settings):
    service = JWTTokenService(settings)
    pair = await service.generate_tokens(uuid4())

    await service.revoke_token(pair.access_token)
    payload = await service.verify_token(pair.access_token)

    assert payload is None
