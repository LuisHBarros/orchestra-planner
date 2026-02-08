"""Integration tests for roles router auth requirements."""

import pytest


@pytest.mark.asyncio
async def test_roles_requires_bearer(api_client):
    res = await api_client.post(
        "/projects/00000000-0000-0000-0000-000000000001/roles",
        json={"name": "Dev"},
    )
    assert res.status_code in {401, 403}
