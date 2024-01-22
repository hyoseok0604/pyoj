import os
from contextlib import AbstractContextManager, suppress
from types import TracebackType

from judger.cgroup.exceptions import CgroupsException
from judger.logger import _log
from judger.utils.mount import get_mount_type


class Cgroup(AbstractContextManager):
    def __init__(self, path: str, name: str) -> None:
        self.path = path
        self.name = name

        self._check_mount()
        self._create_group_directory()

    def get_cpu_time(self) -> int:
        for line in self._read("cpu.stat"):
            key, value = line.split(" ")

            if key == "usage_usec":
                return int(value)
        return -1

    def get_max_memory_usage(self) -> int:
        return int(self._read("memory.peak")[0])

    def get_oom_kill(self) -> int:
        for line in self._read("memory.events"):
            key, value = line.split(" ")

            if key == "oom_kill":
                return int(value)
        return -1

    def set_max_memory_usage(self, max_usage: int):
        self._write("memory.high", str(max_usage * 2))
        self._write("memory.max", str(max_usage))

        self._write("memory.swap.high", "0")
        self._write("memory.swap.max", "0")

    def set_pid(self, pid: int):
        self._write("cgroup.procs", str(pid))

    def __enter__(self):
        return self

    def __exit__(
        self,
        __exc_type: type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None,
    ) -> bool | None:
        try:
            cleanup_target_directory = os.path.join(self.path, self.name)
            # os.rmdir(cleanup_target_directory)
            _log.info(f"Cleanup directory success. {cleanup_target_directory}")
        except Exception as e:
            _log.warn("Failed to remove directory.", exc_info=e)

        return False

    def _check_mount(self):
        if (mount_type := get_mount_type(self.path)) != "cgroup2":
            raise CgroupsException(
                "Expected mount type is cgroup "
                f"but current mount type is {mount_type}."
            )

    def _create_group_directory(self):
        try:
            with suppress(Exception):
                os.rmdir(os.path.join(self.path, self.name))
            os.mkdir(os.path.join(self.path, self.name))
        except Exception as e:
            raise CgroupsException("Failed to create group directory.") from e

    def _read(self, filename: str) -> list[str]:
        try:
            with open(os.path.join(self.path, self.name, filename)) as f:
                return f.readlines()
        except Exception as e:
            raise CgroupsException(f"Failed to read from {filename}.") from e

    def _write(self, filename: str, content: str) -> None:
        try:
            with open(os.path.join(self.path, self.name, filename), "w") as f:
                f.write(content)
        except Exception as e:
            raise CgroupsException(f"Failed to write into {filename}.") from e
