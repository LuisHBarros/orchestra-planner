"""End-to-end tests for auth and project/task flows."""

from __future__ import annotations

import re

import pytest


async def _login_with_magic_link(client, email: str) -> dict:
    req = await client.post("/auth/magic-link", json={"email": email})
    assert req.status_code == 204

    debug = await client.get("/auth/debug/last-magic-link")
    assert debug.status_code == 200
    body_text = debug.json()["body_text"]
    body_html = debug.json()["body_html"]
    match = re.search(r"\\?token=([A-Za-z0-9_-]+)", body_html)
    if match is None:
        match = re.search(r"Click here to login: ([A-Za-z0-9_-]+)", body_text)
    assert match is not None

    verify = await client.post("/auth/verify", json={"token": match.group(1)})
    assert verify.status_code == 200, verify.text
    payload = verify.json()
    assert "access_token" in payload
    assert "refresh_token" in payload
    return payload


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_e2e_auth_refresh_revoke_cycle(e2e_client):
    tokens = await _login_with_magic_link(e2e_client, "manager@example.com")

    refreshed = await e2e_client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refreshed.status_code == 200
    refreshed_payload = refreshed.json()
    assert refreshed_payload["access_token"] != tokens["access_token"]
    assert refreshed_payload["refresh_token"] != tokens["refresh_token"]

    protected = await e2e_client.post(
        "/projects",
        json={"name": "Auth E2E Project", "description": ""},
        headers=_bearer(refreshed_payload["access_token"]),
    )
    assert protected.status_code == 201

    revoke = await e2e_client.post(
        "/auth/revoke",
        json={"refresh_token": refreshed_payload["refresh_token"]},
    )
    assert revoke.status_code == 204

    refresh_after_revoke = await e2e_client.post(
        "/auth/refresh",
        json={"refresh_token": refreshed_payload["refresh_token"]},
    )
    assert refresh_after_revoke.status_code == 401


@pytest.mark.asyncio
async def test_e2e_manager_employee_project_task_flow(e2e_client):
    manager_tokens = await _login_with_magic_link(e2e_client, "manager2@example.com")
    employee_tokens = await _login_with_magic_link(e2e_client, "employee2@example.com")

    create_project = await e2e_client.post(
        "/projects",
        json={"name": "E2E Project", "description": "full flow"},
        headers=_bearer(manager_tokens["access_token"]),
    )
    assert create_project.status_code == 201
    project_id = create_project.json()["id"]

    configure_calendar = await e2e_client.post(
        f"/projects/{project_id}/calendar",
        json={"timezone": "UTC", "exclusion_dates": ["2026-02-15"]},
        headers=_bearer(manager_tokens["access_token"]),
    )
    assert configure_calendar.status_code == 204

    create_role = await e2e_client.post(
        f"/projects/{project_id}/roles",
        json={"name": "Backend Developer"},
        headers=_bearer(manager_tokens["access_token"]),
    )
    assert create_role.status_code == 201
    role_id = create_role.json()["id"]

    create_invite = await e2e_client.post(
        f"/projects/{project_id}/invites",
        json={"role_id": role_id},
        headers=_bearer(manager_tokens["access_token"]),
    )
    assert create_invite.status_code == 201
    invite_token = create_invite.json()["invite"]["token"]

    accept_invite = await e2e_client.post(
        f"/invites/{invite_token}/accept",
        json={"seniority_level": "Mid"},
        headers=_bearer(employee_tokens["access_token"]),
    )
    assert accept_invite.status_code == 201

    create_task_a = await e2e_client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Task A", "description": "A", "difficulty_points": 3},
        headers=_bearer(manager_tokens["access_token"]),
    )
    assert create_task_a.status_code == 201
    task_a_id = create_task_a.json()["id"]

    create_task_b = await e2e_client.post(
        f"/projects/{project_id}/tasks",
        json={"title": "Task B", "description": "B", "difficulty_points": 2},
        headers=_bearer(manager_tokens["access_token"]),
    )
    assert create_task_b.status_code == 201
    task_b_id = create_task_b.json()["id"]

    add_dependency = await e2e_client.post(
        f"/projects/{project_id}/tasks/{task_b_id}/dependencies",
        json={"blocking_task_id": task_a_id},
        headers=_bearer(manager_tokens["access_token"]),
    )
    assert add_dependency.status_code == 201

    remove_dependency = await e2e_client.delete(
        f"/projects/{project_id}/tasks/{task_b_id}/dependencies/{task_a_id}",
        headers=_bearer(manager_tokens["access_token"]),
    )
    assert remove_dependency.status_code == 200

    select_task = await e2e_client.post(
        f"/projects/{project_id}/tasks/{task_a_id}/select",
        headers=_bearer(employee_tokens["access_token"]),
    )
    assert select_task.status_code == 200
    assert select_task.json()["status"] == "Doing"

    add_report = await e2e_client.post(
        f"/projects/{project_id}/tasks/{task_a_id}/reports",
        json={"report_text": "Work in progress"},
        headers=_bearer(employee_tokens["access_token"]),
    )
    assert add_report.status_code == 201

    complete_task = await e2e_client.post(
        f"/projects/{project_id}/tasks/{task_a_id}/complete",
        headers=_bearer(employee_tokens["access_token"]),
    )
    assert complete_task.status_code == 200
    assert complete_task.json()["status"] == "Done"

    cancel_task = await e2e_client.post(
        f"/projects/{project_id}/tasks/{task_b_id}/cancel",
        headers=_bearer(manager_tokens["access_token"]),
    )
    assert cancel_task.status_code == 200
    assert cancel_task.json()["status"] == "Cancelled"

    delete_task = await e2e_client.delete(
        f"/projects/{project_id}/tasks/{task_b_id}",
        headers=_bearer(manager_tokens["access_token"]),
    )
    assert delete_task.status_code == 204
