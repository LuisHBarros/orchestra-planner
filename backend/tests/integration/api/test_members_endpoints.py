"""Integration tests for members router auth requirements."""

import pytest


@pytest.mark.asyncio
async def test_members_requires_bearer(api_client):
    res = await api_client.delete(
        "/projects/00000000-0000-0000-0000-000000000001/members/00000000-0000-0000-0000-000000000002"
    )
    assert res.status_code in {401, 403}


@pytest.mark.asyncio
async def test_members_list_requires_bearer(api_client):
    res = await api_client.get(
        "/projects/00000000-0000-0000-0000-000000000001/members?limit=20&offset=0"
    )
    assert res.status_code in {401, 403}
