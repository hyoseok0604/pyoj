import shlex
import subprocess

from ..logger import _log
from .result import CompileResult


def compile(
    working_directory: str, compile_command: str, timeout: int
) -> CompileResult:
    try:
        with subprocess.Popen(
            args=shlex.split(compile_command), cwd=working_directory
        ) as compile_process:
            try:
                compile_process.wait(timeout)
            except subprocess.TimeoutExpired:
                _log.info(
                    "Compile failed due to timeout. "
                    "Current timeout is {timeout} second(s)."
                )
                compile_process.kill()
                return CompileResult.COMPILE_FAILURE
    except Exception as e:
        _log.info("Compile failed", exc_info=e)
        return CompileResult.COMPILE_FAILURE
    else:
        if compile_process.returncode == 0:
            _log.info("Compile success.")
            return CompileResult.COMPILE_SUCCESS
        else:
            _log.info(f"Compile failure. Return code is {compile_process.returncode}")
            return CompileResult.COMPILE_FAILURE
