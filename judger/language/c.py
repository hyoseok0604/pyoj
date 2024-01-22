from judger.language.base import Language

C11 = Language(
    filename="main.c",
    compile_command="/usr/bin/gcc main.c -o main -O2 -lm -static -std=gnu11",
    execute_command="./main",
)
