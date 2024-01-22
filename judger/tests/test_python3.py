from pathlib import Path

from judger import compile, execute
from judger.compile.result import CompileResult
from judger.execute.result import ExecuteResult
from judger.language import PYTHON3


def test_python3_good(tmp_path: Path):
    language = PYTHON3
    code = """
a, b = map(int, input().split())
print(a + b)
"""

    source_file = tmp_path / language.filename
    source_file.write_text(code)

    stdin_file = tmp_path / "0.in"
    stdin_file.write_text("1 2\n")

    compile_result = compile(tmp_path.as_posix(), language.compile_command, 1)

    assert compile_result == CompileResult.COMPILE_SUCCESS

    execute_result, _, _ = execute(
        tmp_path.as_posix(),
        language.execute_command,
        stdin_file.as_posix(),
        "0.out",
        1000,
        512 * 1024 * 1024,
        64 * 1024 * 1024,
        {i: True for i in range(500)},
    )

    assert execute_result == ExecuteResult.GOOD

    stdout_file = tmp_path / "0.out"
    assert stdout_file.read_text() == "3\n"


def test_python3_time_limit_exceeded(tmp_path: Path):
    language = PYTHON3
    code = """
while True:
    pass
"""

    source_file = tmp_path / language.filename
    source_file.write_text(code)

    stdin_file = tmp_path / "0.in"
    stdin_file.write_text("1 2\n")

    compile_result = compile(tmp_path.as_posix(), language.compile_command, 1)

    assert compile_result == CompileResult.COMPILE_SUCCESS

    execute_result, _, _ = execute(
        tmp_path.as_posix(),
        language.execute_command,
        stdin_file.as_posix(),
        "0.out",
        1000,
        512 * 1024 * 1024,
        64 * 1024 * 1024,
        {i: True for i in range(500)},
    )

    assert execute_result == ExecuteResult.TIME_LIMIT_EXCEEDED
