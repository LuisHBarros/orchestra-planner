"""Integration tests for PostgresUserRepository."""

from backend.src.adapters.db import PostgresUserRepository
from backend.src.domain.entities import User


import pytest


@pytest.mark.asyncio
async def test_user_repository_roundtrip(db_session):
    repo = PostgresUserRepository(db_session)
    user = User(email="user@example.com", name="User")
    user.generate_magic_link_token()

    await repo.save(user)

    by_id = await repo.find_by_id(user.id)
    by_email = await repo.find_by_email("USER@example.com")
    by_hash = await repo.find_by_magic_link_token_hash(user.magic_link_token_hash)

    assert by_id is not None
    assert by_email is not None
    assert by_hash is not None
    assert by_email.id == user.id
