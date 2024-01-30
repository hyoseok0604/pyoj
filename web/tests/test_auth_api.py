import pytest


@pytest.mark.anyio
async def test_auth_api(client, monkeypatch_response_set_cookie):
    response = await client.get("/api/me")
    assert response.status_code == 401

    response = await client.post(
        "/api/users",
        json={
            "username": "username",
            "password1": "password",
            "password2": "password",
        },
    )
    id = response.json().get("id")

    response = await client.post(
        "/api/login",
        json={
            "username": "username",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401

    response = await client.post(
        "/api/login",
        json={
            "username": "username",
            "password": "password",
        },
    )
    assert response.status_code == 204
    assert response.cookies.get("session") is not None

    response = await client.get("/api/me")
    assert response.status_code == 200
    assert response.json().get("id") == id
    assert response.json().get("username") == "username"

    response = await client.post("/api/logout")
    assert response.status_code == 204
    assert response.cookies.get("session") is None

    response = await client.get("/api/me")
    assert response.status_code == 401
