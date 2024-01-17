import ctypes
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:

    class PtraceSyscallInfoBase:
        arch: int
        instruction_pointer: int
        stack_pointer: int

    class Entry:
        nr: int
        args: ctypes.Array[ctypes.c_uint64]

    class Exit:
        rval: int
        is_error: int

    class Seccomp:
        nr: int
        args: ctypes.Array[ctypes.c_uint64]
        ret_data: int

    class PtraceSyscallInfoNone(PtraceSyscallInfoBase):
        op: Literal[0]

    class PtraceSyscallInfoEntry(PtraceSyscallInfoBase):
        op: Literal[1]
        entry: Entry

    class PtraceSyscallInfoExit(PtraceSyscallInfoBase):
        op: Literal[2]
        exit: Exit

    class PtraceSyscallInfoSeccomp(PtraceSyscallInfoBase):
        op: Literal[3]
        seccomp: Seccomp

    class PtraceSyscallInfo(ctypes.Structure):
        pass

    TPtraceSyscallInfo = (
        PtraceSyscallInfoEntry | PtraceSyscallInfoExit | PtraceSyscallInfoSeccomp
    )
else:

    class Entry(ctypes.Structure):
        _fields_ = [
            ("nr", ctypes.c_uint64),
            ("args", ctypes.c_uint64 * 6),
        ]

    class Exit(ctypes.Structure):
        _fields_ = [
            ("rval", ctypes.c_int64),
            ("is_error", ctypes.c_uint8),
        ]

    class Seccomp(ctypes.Structure):
        _fields_ = [
            ("nr", ctypes.c_uint64),
            ("args", ctypes.c_uint64 * 6),
            ("ret_data", ctypes.c_uint32),
        ]

    class SyscallInfo(ctypes.Union):
        _fields_ = [
            ("entry", Entry),
            ("exit", Exit),
            ("seccomp", Seccomp),
        ]

    class PtraceSyscallInfo(ctypes.Structure):
        _anonymous_ = ["_info"]
        _fields_ = [
            ("op", ctypes.c_uint8),
            ("arch", ctypes.c_uint32),
            ("instruction_pointer", ctypes.c_uint64),
            ("stack_pointer", ctypes.c_uint64),
            ("_info", SyscallInfo),
        ]

    TPtraceSyscallInfo = PtraceSyscallInfo
