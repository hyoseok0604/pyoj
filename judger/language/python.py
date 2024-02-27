from judger.language.base import Language

PYTHON3 = Language(
    display_name="Python 3",
    filename="main.py",
    compile_command="/usr/local/bin/python3 -W ignore -c \"import py_compile; py_compile.compile(r'main.py')\"",  # noqa: E501
    execute_command="/usr/local/bin/python3 -W ignore main.py",
)
