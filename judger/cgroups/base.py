import os

from judger.cgroups.exceptions import CgroupsException
from judger.logger import _log
from judger.utils.mount import get_mount_options, get_mount_type


class BaseCgroups:
    def __init__(self, path: str, name: str, subsystem: str) -> None:
        self.path = path
        self.name = name
        self.subsystem = subsystem

        self._check_mount()

    def set_pid(self, pid: int):
        self._write("cgroup.procs", str(pid))

    def __enter__(self):
        return self

    def __exit__(self):
        try:
            os.rmdir(os.path.join(self.path, self.name))
        except Exception as e:
            _log.warn("Failed to remove directory.", exc_info=e)

    def _check_mount(self):
        if (mount_type := get_mount_type(self.path)) != "cgroups":
            raise CgroupsException(
                "Expected mount type is cgroups "
                f"but current mount type is {mount_type}."
            )

        if (
            mount_options := get_mount_options(self.path)
        ) is None or self.subsystem not in mount_options.split(","):
            raise CgroupsException(f"Mount options must contain {self.subsystem}.")

    def _create_group_directory(self):
        try:
            os.mkdir(os.path.join(self.path, self.name))
        except Exception as e:
            raise CgroupsException("Failed to create group directory.") from e

    def _read(self, filename: str) -> list[str]:
        try:
            with open(os.path.join(self.path, self.name, filename)) as f:
                return f.readlines()
        except Exception as e:
            raise CgroupsException(f"Failed to read operation from {filename}.") from e

    def _write(self, filename: str, content: str) -> None:
        try:
            with open(os.path.join(self.path, self.name, filename), "w") as f:
                f.write(content)
        except Exception as e:
            raise CgroupsException(f"Failed to write operation into {filename}.") from e
