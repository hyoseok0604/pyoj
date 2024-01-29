from typing import Any, TypeGuard

import pytest


@pytest.mark.parametrize(
    "username,username_error_type",
    [
        ("good123", None),
        ("short", "username_length"),
        ("longlonglonglonglonglonglong", "username_length"),
        ("bad username!@#", "username_not_alphanumeric"),
    ],
)
@pytest.mark.parametrize(
    "password1,password1_error_type",
    [
        ("good123@", None),
        ("short", "password_length"),
        ("longlonglonglonglonglonglong", "password_length"),
        ("white space ", "password_not_printable"),
    ],
)
@pytest.mark.parametrize(
    "password2",
    ["good123@", "short", "longlonglonglonglonglonglong", "white space "],
)
@pytest.mark.anyio
async def test_create_user_api(
    client,
    username,
    username_error_type,
    password1,
    password1_error_type,
    password2,
):
    response = await client.post(
        "/api/users",
        json={
            "username": username,
            "password1": password1,
            "password2": password2,
        },
    )

    error_types = [username_error_type, password1_error_type]

    if all(v is None for v in error_types):
        if password1 == password2:
            assert response.status_code == 201
            assert response.json().get("username") == username
        else:
            assert response.status_code == 422
            assert response.json().get("detail")[0].get("type") == "password_not_match"
    else:
        details = response.json().get("detail")

        def get_type(error: Any) -> str:
            return error.get("type")

        def not_none(val: str | None) -> TypeGuard[str]:
            return val is not None

        error_types = list(filter(not_none, error_types))
        error_types.sort()
        response_error_types = list(map(get_type, details))
        response_error_types.sort()

        assert response.status_code == 422
        assert response_error_types == error_types


@pytest.mark.anyio
async def test_create_user_api_duplicated_username(client):
    await client.post(
        "/api/users",
        json={
            "username": "username",
            "password1": "password",
            "password2": "password",
        },
    )

    response = await client.post(
        "/api/users",
        json={
            "username": "username",
            "password1": "password",
            "password2": "password",
        },
    )

    assert response.status_code == 422
    assert response.json() == {"username": "이미 존재하는 아이디입니다."}
