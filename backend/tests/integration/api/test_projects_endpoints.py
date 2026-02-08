"""Integration tests for projects router auth requirements."""

import pytest


@pytest.mark.asyncio
async def test_projects_requires_bearer(api_client):
    res = await api_client.post("/projects", json={"name": "P", "description": ""})
    assert res.status_code in {401, 403}
