import re
from typing import TypedDict


class Systemcall(TypedDict):
    name: str
    number: int


def parse_systemcall_x86_64_linux_gnu() -> list[Systemcall]:
    systemcalls = []

    with open("/usr/include/x86_64-linux-gnu/asm/unistd_64.h") as f:
        pattern = r"#define\s+__NR_(\w+)\s+(\d+)"
        for line in f:
            match = re.search(pattern, line)
            if match and len(match.groups()) == 2:
                name, number = match.groups()
                number = int(number)

                systemcalls.append(Systemcall(name=name, number=number))

    return systemcalls
