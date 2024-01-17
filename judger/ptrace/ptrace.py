import ctypes

_libc = ctypes.CDLL("/lib/x86_64-linux-gnu/libc.so.6")
ptrace = _libc.ptrace
ptrace.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]
ptrace.restype = ctypes.c_int
