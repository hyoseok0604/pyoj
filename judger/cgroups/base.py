import os
from contextlib import AbstractContextManager, suppress
from types import TracebackType

from judger.cgroups.exceptions import CgroupsException
from judger.logger import _log
from judger.utils.mount import get_mount_options, get_mount_type


class BaseCgroups(AbstractContextManager):
    __namespace = "judger"

    def __init__(self, path: str, name: str, subsystem: str) -> None:
        self.path = path
        self.name = name
        self.subsystem = subsystem

        self._check_mount()
        self._create_namespace()
        self._create_group_directory()

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
            cleanup_target_directory = os.path.join(
                self.path, self.__namespace, self.name
            )
            os.rmdir(cleanup_target_directory)
            _log.info(f"Cleanup directory success. {cleanup_target_directory}")
        except Exception as e:
            _log.warn("Failed to remove directory.", exc_info=e)

        return False

    def _check_mount(self):
        if (mount_type := get_mount_type(self.path)) != "cgroup":
            raise CgroupsException(
                "Expected mount type is cgroup "
                f"but current mount type is {mount_type}."
            )

        if (
            mount_options := get_mount_options(self.path)
        ) is None or self.subsystem not in mount_options.split(","):
            raise CgroupsException(f"Mount options must contain {self.subsystem}.")

    def _create_namespace(self):
        with suppress(FileExistsError):
            os.mkdir(os.path.join(self.path, self.__namespace))

    def _create_group_directory(self):
        try:
            os.mkdir(os.path.join(self.path, self.__namespace, self.name))
        except Exception as e:
            raise CgroupsException("Failed to create group directory.") from e

    def _read(self, filename: str) -> list[str]:
        try:
            with open(
                os.path.join(self.path, self.__namespace, self.name, filename)
            ) as f:
                return f.readlines()
        except Exception as e:
            raise CgroupsException(f"Failed to read from {filename}.") from e

    def _write(self, filename: str, content: str) -> None:
        try:
            with open(
                os.path.join(self.path, self.__namespace, self.name, filename), "w"
            ) as f:
                f.write(content)
        except Exception as e:
            raise CgroupsException(f"Failed to write into {filename}.") from e
