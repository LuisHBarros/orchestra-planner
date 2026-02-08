"""Integration tests for invites router auth requirements."""

import pytest


@pytest.mark.asyncio
async def test_invites_create_requires_bearer(api_client):
    res = await api_client.post(
        "/projects/00000000-0000-0000-0000-000000000001/invites",
        json={"role_id": "00000000-0000-0000-0000-000000000002"},
    )
    assert res.status_code in {401, 403}
