import functools

from judger.ptrace.constants import PtraceRequest
from judger.ptrace.exceptions import PtraceException


def raise_on_ptrace_fail(request: PtraceRequest):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return_value = func(*args, **kwargs)
            if return_value == -1:
                raise PtraceException(request)

        return wrapper

    return decorator
