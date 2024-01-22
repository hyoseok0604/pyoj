import math
import os
import resource
import shlex
import signal
import stat
from pty import STDERR_FILENO, STDIN_FILENO, STDOUT_FILENO
from typing import Never

from judger.cgroup import Cgroup
from judger.execute.exceptions import ExecuteException
from judger.execute.result import ExecuteResult
from judger.logger import _log
from judger.ptrace import (
    PtraceEvents,
    PtraceOptions,
    ptrace_cont,
    ptrace_get_syscall_info,
    ptrace_set_options,
    ptrace_syscall,
    ptrace_trace_me,
)


def execute(
    working_directory: str,
    execute_command: str,
    stdin_filename: str,
    stdout_filename: str,
    time_limit: int,
    memory_limit: int,
    output_limit: int,
    is_syscall_allowed: dict[int, bool],
):
    try:
        os.chdir(working_directory)

        pid = os.fork()
    except Exception as e:
        raise ExecuteException() from e

    if pid == 0:
        _execute_child(
            execute_command, stdin_filename, stdout_filename, time_limit, output_limit
        )
    else:
        return _execute_parent(pid, time_limit, memory_limit, is_syscall_allowed)


def _execute_child(
    execute_command: str,
    stdin_filename: str,
    stdout_filename: str,
    time_limit: int,
    output_limit: int,
) -> Never:
    fdin = os.open(stdin_filename, os.O_RDONLY)
    os.dup2(fdin, STDIN_FILENO)
    os.close(fdin)

    fdout = os.open(
        stdout_filename,
        # os.devnull,
        os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
        stat.S_IWUSR | stat.S_IRUSR,
    )
    os.dup2(fdout, STDOUT_FILENO)
    os.close(fdout)

    fderr = os.open(os.devnull, os.O_WRONLY)
    os.dup2(fderr, STDERR_FILENO)
    os.close(fderr)

    command = shlex.split(execute_command)

    resource.setrlimit(
        resource.RLIMIT_CPU,
        (math.ceil(time_limit / 1000), math.ceil(time_limit / 1000) + 1),
    )
    resource.setrlimit(resource.RLIMIT_FSIZE, (output_limit, output_limit))

    ptrace_trace_me()
    env: dict[str, str] = {}
    os.execve(command[0], command, env)


def _execute_parent(
    pid: int, time_limit: int, memory_limit: int, is_syscall_allowed: dict[int, bool]
):
    result: ExecuteResult | None = None
    time = 0
    memory = 0

    _handle_execve_under_ptrace(pid)

    with Cgroup("/sys/fs/cgroup", str(pid)) as cgroup:
        cgroup.set_pid(pid)
        cgroup.set_max_memory_usage(memory_limit)

        while True:
            _, status = os.waitpid(pid, 0)

            if os.WIFEXITED(status):
                if os.WEXITSTATUS(status) == 0:
                    result = ExecuteResult.GOOD
                    _log.info("Exit code is zero. All is good.")
                    break
                else:
                    result = ExecuteResult.NON_ZERO_EXIT_CODE
                    _log.info("Exit code is non zero.")
                    break

            if os.WIFSIGNALED(status):
                if result is not None:
                    break

                result = _termsig_to_execute_result(
                    status,
                    cgroup,
                    time_limit,
                )
                break

            if os.WIFSTOPPED(status):
                if os.WSTOPSIG(status) == signal.SIGTRAP | 0x80:
                    syscall_info = ptrace_get_syscall_info(pid)

                    if syscall_info.op == 1:
                        syscall_number = syscall_info.entry.nr

                        if syscall_number not in is_syscall_allowed:
                            result = ExecuteResult.UNKNOWN_SYSCALL
                            _log.info(
                                "Unable to check "
                                f"if system call({syscall_number}) is allowed."
                            )

                        if not is_syscall_allowed[syscall_number]:
                            result = ExecuteResult.NOT_ALLOWED_SYSCALL
                            _log.info(f"System call({syscall_number}) is not allowed.")

                elif status >> 8 == (
                    signal.SIGTRAP | PtraceEvents.PTRACE_EVENT_EXIT << 8
                ):
                    _log.info("Handle ptrace event exit.")

                    time = cgroup.get_cpu_time() // 1000
                    memory = cgroup.get_max_memory_usage()

                    ptrace_cont(pid)
                    continue

                elif os.WSTOPSIG(status) == signal.SIGXFSZ:
                    _log.info("Output limit exceeded.")
                    result = ExecuteResult.OUTPUT_LIMIT_EXCEEDED

                elif os.WSTOPSIG(status) == signal.SIGXCPU:
                    _log.info("Time limit exceeded.")
                    result = ExecuteResult.TIME_LIMIT_EXCEEDED

            if result is not None:
                # Result already determined. Kill child process.
                os.kill(pid, signal.SIGKILL)
                _log.debug(f"Result is set to {result} Kill process.")
                continue

            ptrace_syscall(pid)

    return result, time, memory


def _handle_execve_under_ptrace(pid: int):
    _, status = os.waitpid(pid, 0)

    if os.WIFSTOPPED(status) and os.WSTOPSIG(status) == signal.SIGTRAP:
        _log.info("Handle execve under ptrace success.")

        ptrace_option = (
            PtraceOptions.PTRACE_O_TRACESYSGOOD
            | PtraceOptions.PTRACE_O_EXITKILL
            | PtraceOptions.PTRACE_O_TRACEEXIT
        )

        ptrace_set_options(pid, ptrace_option)
        ptrace_syscall(pid)
    else:
        raise ExecuteException("Failed to handle execve under ptrace.")


def _termsig_to_execute_result(
    status: int,
    cgroup: Cgroup,
    time_limit: int,
) -> ExecuteResult:
    sig = os.WTERMSIG(status)

    if sig == signal.SIGKILL:
        if cgroup.get_oom_kill() == 1:
            _log.info("Memory limit exceeded.")
            return ExecuteResult.MEMORY_LIMIT_EXCEEDED
        if cgroup.get_cpu_time() >= time_limit:
            _log.info("Time limit exceeded.")
            return ExecuteResult.TIME_LIMIT_EXCEEDED

    _log.info(f"Signaled({sig}).")
    return ExecuteResult.RUNTIME_ERROR
