import pytest

from web.services.file import FileService
from web.tests.conftest import FixtureProblem

pytestmark = [
    pytest.mark.anyio,
    pytest.mark.usefixtures("create_users", "create_problems"),
]


@pytest.mark.parametrize("create_problems", [{"creators": [0]}], indirect=True)
@pytest.mark.parametrize("input_too_large", [True, False])
@pytest.mark.parametrize("output_too_large", [True, False])
async def test_create_testcase_api_too_large_testcase_file(
    client,
    login,
    create_problems: list[FixtureProblem],
    monkeypatch,
    input_too_large,
    output_too_large,
):
    monkeypatch.setattr(FileService, "TEST_CASE_FILE_SIZE_LIMIT", 2 * 1024)

    if not input_too_large and not output_too_large:
        return

    await login(0)

    large_testcase = b"a" * 3 * 1024
    good_testcase = b"a" * 1024

    response = await client.post(
        f"/api/problems/{create_problems[0]['id']}/testcases",
        files={
            "input_file": large_testcase if input_too_large else good_testcase,
            "output_file": large_testcase if output_too_large else good_testcase,
        },
    )

    assert response.status_code == 413

    assert (response.json().get("input_file") is None) != input_too_large
    assert (response.json().get("output_file") is None) != output_too_large


@pytest.mark.parametrize("create_problems", [{"creators": [0]}], indirect=True)
async def test_create_testcase_api_good(
    client, login, create_problems: list[FixtureProblem]
):
    await login(0)

    good_testcase = b"a" * 1024

    response = await client.post(
        f"/api/problems/{create_problems[0]['id']}/testcases",
        files={"input_file": good_testcase, "output_file": good_testcase},
    )

    assert response.status_code == 201


@pytest.mark.parametrize("create_problems", [{"creators": [0]}], indirect=True)
async def test_create_testcase_api_without_login(
    client, create_problems: list[FixtureProblem]
):
    good_testcase = b"a" * 1024

    response = await client.post(
        f"/api/problems/{create_problems[0]['id']}/testcases",
        files={"input_file": good_testcase, "output_file": good_testcase},
    )

    assert response.status_code == 401


@pytest.mark.parametrize("create_users", [{"count": 2}], indirect=True)
@pytest.mark.parametrize("create_problems", [{"creators": [0]}], indirect=True)
async def test_create_testcase_api_other_user_problem(
    client, login, create_problems: list[FixtureProblem]
):
    await login(1)

    good_testcase = b"a" * 1024

    response = await client.post(
        f"/api/problems/{create_problems[0]['id']}/testcases",
        files={"input_file": good_testcase, "output_file": good_testcase},
    )

    assert response.status_code == 403


async def test_create_testcase_api_wrong_problem_id(client, login):
    await login(0)

    good_testcase = b"a" * 1024

    response = await client.post(
        "/api/problems/1/testcases",
        files={"input_file": good_testcase, "output_file": good_testcase},
    )

    assert response.status_code == 404


@pytest.mark.parametrize("create_problems", [{"creators": [0]}], indirect=True)
async def test_craete_testcase_api_generate_preview_correct(
    client, login, create_problems: list[FixtureProblem]
):
    await login(0)

    original_testcase = (
        b"   1 2 3   \n\t    123213\n\n\n\n\n\n\n\n\n\n\n3\n4\n5\n6\n7\n8\n9\n10\n11\n"
    )

    response = await client.post(
        f"/api/problems/{create_problems[0]["id"]}/testcases",
        files={"input_file": original_testcase, "output_file": original_testcase},
    )

    assert response.status_code == 201
    assert (
        response.json().get("input_preview") == "1 2 3\n123213\n3\n4\n5\n6\n7\n8\n9\n10"
    )
