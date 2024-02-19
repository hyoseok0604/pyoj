import pytest

pytestmark = [
    pytest.mark.anyio,
    pytest.mark.usefixtures("create_users"),
]


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


async def test_create_problem_api_success(client, login):
    await login(0)
    response = await client.post("/api/problems", json=simple_problem)

    assert response.status_code == 201

    for k, v in simple_problem.items():
        assert response.json().get(k) == v


async def test_update_problem_api_not_found(client, login):
    await login(0)

    response = await client.patch("/api/problems/123", json={"time_limit": 500})

    assert response.status_code == 404


async def test_update_problem_api_success(client, login):
    await login(0)

    update_problem = {
        "time_limit": 500,
        "memory_limit": 256,
    }

    response = await client.post(
        "/api/problems",
        json=simple_problem,
    )

    id = response.json().get("id")

    expect_problem = simple_problem.copy()
    expect_problem.update(update_problem)

    response = await client.patch(
        f"/api/problems/{id}",
        json={
            "time_limit": 500,
            "memory_limit": 256,
        },
    )

    assert response.status_code == 200
    for k, v in expect_problem.items():
        assert response.json().get(k) == v


async def test_delete_problem_api_success(client, login):
    await login(0)

    response = await client.post("/api/problems", json=simple_problem)

    id = response.json().get("id")

    response = await client.delete(f"/api/problems/{id}")

    assert response.status_code == 204


@pytest.mark.parametrize("create_users", [{"count": 2}], indirect=True)
async def test_delete_problem_api_permission_forbidden(client, login):
    await login(0)

    response = await client.post("/api/problems", json=simple_problem)

    id = response.json().get("id")

    await login(1)

    response = await client.delete(f"/api/problems/{id}")

    assert response.status_code == 403
