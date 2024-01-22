import enum


class ExecuteResult(enum.Enum):
    GOOD = "good"
    NON_ZERO_EXIT_CODE = "non_zero_exit_code"
    RUNTIME_ERROR = "runtime_error"

    # Limit Exceeded
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    OUTPUT_LIMIT_EXCEEDED = "output_limit_exceeded"

    # System Call
    UNKNOWN_SYSCALL = "unknown_syscall"
    NOT_ALLOWED_SYSCALL = "not_allowed_syscall"

    # Exception
    ERROR = "error"
