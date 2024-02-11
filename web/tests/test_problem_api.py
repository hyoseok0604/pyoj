import pytest

pytestmark = [pytest.mark.anyio, pytest.mark.usefixtures("create_user")]


simple_problem = {
    "title": "title",
    "time_limit": 1000,
    "memory_limit": 256,
    "description": "description",
    "input_description": "input_description",
    "output_description": "output_description",
    "limit_description": "limit_description",
}


async def test_create_problem_api_unauthorized(client):
    response = await client.post(
        "/api/problems",
        json=simple_problem,
    )

    assert response.status_code == 401


async def test_create_problem_api_success(logged_in_client, create_user):
    response = await logged_in_client.post("/api/problems", json=simple_problem)

    assert response.status_code == 201
    assert response.json().get("creator").get("id") == create_user.get("id")
    assert response.json().get("creator").get("username") == create_user.get("username")


async def test_update_problem_api_not_found(logged_in_client):
    response = await logged_in_client.patch(
        "/api/problems/123", json={"time_limit": 500}
    )

    assert response.status_code == 404


async def test_update_problem_api_success(logged_in_client):
    response = await logged_in_client.post(
        "/api/problems",
        json=simple_problem,
    )

    id = response.json().get("id")

    response = await logged_in_client.patch(
        f"/api/problems/{id}",
        json={
            "time_limit": 500,
            "memory_limit": 256,
        },
    )

    assert response.status_code == 200
    assert response.json().get("title") == "title"
    assert response.json().get("time_limit") == 500


async def test_delete_problem_api_success(logged_in_client):
    response = await logged_in_client.post("/api/problems", json=simple_problem)

    id = response.json().get("id")

    response = await logged_in_client.delete(f"/api/problems/{id}")

    assert response.status_code == 204
