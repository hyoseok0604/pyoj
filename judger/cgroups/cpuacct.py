from judger.cgroups.base import BaseCgroups


class CpuacctCgroups(BaseCgroups):
    def __init__(self, path: str, name: str) -> None:
        super().__init__(path, name, "cpuacct")

    def get_cpu_time(self) -> int:
        """Return cpu time in milliseconds"""
        return int(int(self._read("cpuacct.usage")[0]) * 10**-6)
