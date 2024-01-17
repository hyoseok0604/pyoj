import ctypes

from judger.ptrace.constants import PtraceRequest
from judger.ptrace.decorators import raise_on_ptrace_fail
from judger.ptrace.exceptions import PtraceException
from judger.ptrace.ptrace import ptrace
from judger.ptrace.types import PtraceSyscallInfo, TPtraceSyscallInfo


@raise_on_ptrace_fail(PtraceRequest.PTRACE_TRACEME)
def ptrace_trace_me() -> int:
    return ptrace(PtraceRequest.PTRACE_TRACEME, 0, None, None)


@raise_on_ptrace_fail(PtraceRequest.PTRACE_SYSCALL)
def ptrace_syscall(pid: int) -> int:
    return ptrace(PtraceRequest.PTRACE_SYSCALL, pid, None, None)


@raise_on_ptrace_fail(PtraceRequest.PTRACE_SETOPTIONS)
def ptrace_set_options(pid: int, options: int) -> int:
    return ptrace(PtraceRequest.PTRACE_SETOPTIONS, pid, None, options)


@raise_on_ptrace_fail(PtraceRequest.PTRACE_CONT)
def ptrace_cont(pid: int, data: int = 0) -> int:
    return ptrace(PtraceRequest.PTRACE_CONT, pid, None, data)


def ptrace_get_syscall_info(pid: int) -> TPtraceSyscallInfo:
    ptrace_syscall_info = PtraceSyscallInfo()
    result = ptrace(
        PtraceRequest.PTRACE_GET_SYSCALL_INFO,
        pid,
        ctypes.sizeof(ptrace_syscall_info),
        ctypes.byref(ptrace_syscall_info),
    )

    if result == -1:
        raise PtraceException(PtraceRequest.PTRACE_GET_SYSCALL_INFO)

    return ptrace_syscall_info  # type: ignore
