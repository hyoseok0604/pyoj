from dataclasses import dataclass


@dataclass(kw_only=True, frozen=True)
class Language:
    display_name: str
    filename: str
    compile_command: str
    execute_command: str
