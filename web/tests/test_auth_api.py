import pytest

pytestmark = [pytest.mark.anyio, pytest.mark.usefixtures("create_users")]


async def test_login_api_success(client, create_users):
    user = create_users[0]

    response = await client.post(
        "/api/login", json={"username": user["username"], "password": user["password"]}
    )

    assert response.status_code == 204
    assert response.cookies.get("session") is not None


async def test_login_api_wrong_id_or_password(client, create_users):
    user = create_users[0]

    response = await client.post(
        "/api/login",
        json={"username": user["username"], "password": user["password"] + "1"},
    )

    assert response.status_code == 401


async def test_me_api_success(client, create_users):
    user = create_users[0]

    await client.post(
        "/api/login", json={"username": user["username"], "password": user["password"]}
    )

    response = await client.get("/api/me")

    assert response.status_code == 200
    assert response.json().get("id") == user["id"]
    assert response.json().get("username") == user["username"]


async def test_me_api_unauthorized(client):
    response = await client.get("/api/me")

    assert response.status_code == 401


async def test_me_api_deleted_user(client, create_users):
    user = create_users[0]

    await client.post(
        "/api/login", json={"username": user["username"], "password": user["password"]}
    )

    await client.delete(f"/api/users/{user["id"]}")

    response = await client.get("/api/me")

    assert response.status_code == 401


async def test_logout_api(client, create_users):
    user = create_users[0]

    await client.post(
        "/api/login", json={"username": user["username"], "password": user["password"]}
    )

    response = await client.post("/api/logout")

    assert response.status_code == 204
    assert response.cookies.get("session") is None
