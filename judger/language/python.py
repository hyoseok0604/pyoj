from judger.language.base import Language

PYTHON3 = Language(
    filename="main.py",
    compile_command="/usr/local/bin/python3 -W ignore -c \"import py_compile; py_compile.compile(r'main.py')\"",
    execute_command="/usr/local/bin/python3 -W ignore main.py",
)
