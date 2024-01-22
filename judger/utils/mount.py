import os
from contextlib import suppress
from typing import NamedTuple


class FileSystem(NamedTuple):
    fs_spec: str
    fs_file: str
    fs_vfstype: str
    fs_mntops: str
    fs_freq: str
    fs_passno: str


def get_mount_type(path: str) -> str | None:
    filesystem = _get_filesystem_from_mount_point(path)

    return filesystem.fs_vfstype if filesystem is not None else None


def get_mount_options(path: str) -> str | None:
    filesystem = _get_filesystem_from_mount_point(path)

    return filesystem.fs_mntops if filesystem is not None else None


# https://linux.die.net/man/5/fstab
def _get_filesystem_from_mount_point(mount_point: str) -> FileSystem | None:
    with suppress(Exception), open("/etc/mtab") as mtab:
        for line in mtab:
            if line.startswith("#") or line == "":
                continue

            (
                fs_spec,
                fs_file,
                fs_vfstype,
                fs_mntops,
                fs_freq,
                fs_passno,
            ) = line.split(" ")

            if fs_file == os.path.abspath(mount_point):
                return FileSystem(
                    fs_spec, fs_file, fs_vfstype, fs_mntops, fs_freq, fs_passno
                )
    return None
