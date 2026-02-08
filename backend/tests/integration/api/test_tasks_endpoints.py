"""Integration tests for tasks router auth requirements."""

import pytest


@pytest.mark.asyncio
async def test_tasks_requires_bearer(api_client):
    res = await api_client.post(
        "/projects/00000000-0000-0000-0000-000000000001/tasks",
        json={"title": "Task", "description": "", "difficulty_points": 1},
    )
    assert res.status_code in {401, 403}
