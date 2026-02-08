"""Integration tests for auth endpoints."""

import re

import pytest


@pytest.mark.asyncio
async def test_auth_magic_link_verify_refresh_revoke_flow(api_client):
    res = await api_client.post("/auth/magic-link", json={"email": "user@example.com"})
    assert res.status_code == 204

    debug = await api_client.get("/auth/debug/last-magic-link")
    assert debug.status_code == 200
    body_text = debug.json()["body_text"]
    match = re.search(r"Click here to login: (\S+)", body_text)
    assert match is not None
    token = match.group(1)

    verify = await api_client.post("/auth/verify", json={"token": token})
    assert verify.status_code == 200
    payload = verify.json()
    assert "access_token" in payload
    assert "refresh_token" in payload

    refreshed = await api_client.post(
        "/auth/refresh",
        json={"refresh_token": payload["refresh_token"]},
    )
    assert refreshed.status_code == 200

    revoked = await api_client.post(
        "/auth/revoke",
        json={"refresh_token": refreshed.json()["refresh_token"]},
    )
    assert revoked.status_code == 204
