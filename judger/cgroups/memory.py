from contextlib import suppress

from judger.cgroups.base import BaseCgroups


class MemoryCgroups(BaseCgroups):
    def __init__(self, path: str, name: str) -> None:
        super().__init__(path, name, "memory")

    def set_memory_limit(self, memory_limit: int):
        """Set memory limit in bytes"""
        self._write("memory.limit_in_bytes", str(memory_limit))
        self._write("memory.memsw.limit_in_bytes", str(memory_limit))

    def get_memory_usage(self) -> int:
        usage = 0
        for line in self._read("memory.stat"):
            name, value = line.strip().split(" ")

            if name in ["rss", "mapped_file", "cache"]:
                usage += int(value)
        return usage

    def get_stat(self) -> str:
        return "\n".join(self._read("memory.stat"))

    def get_oom_kill_count(self) -> int:
        lines = self._read("memory.oom_control")

        with suppress(Exception):
            for line in lines:
                name, count = line.split(" ")
                count = int(count)
                if name == "oom_kill":
                    return count
        return -1
