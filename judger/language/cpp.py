from judger.language.base import Language

CPP17 = Language(
    display_name="C++17",
    filename="main.cpp",
    compile_command="/usr/bin/g++ main.cpp -o main -O2 -lm -static -std=gnu++17",
    execute_command="./main",
)
