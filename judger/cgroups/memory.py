from contextlib import suppress

from judger.cgroups.base import BaseCgroups


class MemoryCgroups(BaseCgroups):
    def set_memory_limit(self, memory_limit: int):
        """Set memory limit in bytes"""
        self._write("memory.limit_in_bytes", str(memory_limit))
        self._write("memory.memsw.limit_in_bytes", str(memory_limit))

    def get_max_memory_usage(self) -> int:
        return int(self._read("memory.max_usage_in_bytes")[0]) // 1024

    def get_oom_kill_count(self) -> int:
        lines = self._read("memory.oom_control")

        with suppress(Exception):
            for line in lines:
                name, count = line.split(" ")
                count = int(count)
                if name == "oom_kill":
                    return count
        return -1
