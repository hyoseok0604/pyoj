import pytest

pytestmark = [pytest.mark.anyio, pytest.mark.usefixtures("create_user")]


async def test_login_api_success(client):
    response = await client.post(
        "/api/login", json={"username": "username", "password": "password"}
    )

    assert response.status_code == 204
    assert response.cookies.get("session") is not None


async def test_login_api_wrong_id_or_password(client):
    response = await client.post(
        "/api/login", json={"username": "username", "password": "password123"}
    )

    assert response.status_code == 401


async def test_me_api_success(client, create_user):
    await client.post(
        "/api/login", json={"username": "username", "password": "password"}
    )

    response = await client.get("/api/me")

    assert response.status_code == 200
    assert response.json().get("id") == create_user.get("id")
    assert response.json().get("username") == create_user.get("username")


async def test_me_api_unauthorized(client):
    response = await client.get("/api/me")

    assert response.status_code == 401


async def test_me_api_deleted_user(client, create_user):
    await client.post(
        "/api/login", json={"username": "username", "password": "password"}
    )

    await client.delete(f"/api/users/{create_user.get("id")}")

    response = await client.get("/api/me")

    assert response.status_code == 401


async def test_logout_api(client):
    await client.post(
        "/api/login", json={"username": "username", "password": "password"}
    )

    response = await client.post("/api/logout")

    assert response.status_code == 204
    assert response.cookies.get("session") is None
