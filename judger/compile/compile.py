import os
import shlex
import stat
import subprocess

from judger.compile.result import CompileResult
from judger.logger import _log


def compile(
    working_directory: str, compile_command: str, timeout: int
) -> CompileResult:
    _log.info("Compile started.")
    try:
        os.chdir(working_directory)

        stdout = _open("compile_stdout")
        stderr = _open("compile_stderr")

        with subprocess.Popen(
            args=shlex.split(compile_command),
            cwd=working_directory,
            stdout=stdout,
            stderr=stderr,
        ) as compile_process:
            try:
                compile_process.wait(timeout)
            except subprocess.TimeoutExpired:
                _log.info(
                    "Compile failed due to timeout. "
                    f"Current timeout is {timeout} second(s)."
                )
                compile_process.kill()
                return CompileResult.COMPILE_FAILURE
    except Exception as e:
        _log.info("Compile failed due to python exception.", exc_info=e)
        return CompileResult.COMPILE_FAILURE
    else:
        if compile_process.returncode == 0:
            _log.info("Compile success.")
            return CompileResult.COMPILE_SUCCESS
        else:
            _log.info(
                "Compile failed due to compiler. Check stdout, stderr files. "
                f"Compile process return code is {compile_process.returncode}."
            )
            return CompileResult.COMPILE_FAILURE


def _open(filename: str) -> int:
    return os.open(
        filename,
        os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
        stat.S_IWUSR | stat.S_IRUSR,
    )
