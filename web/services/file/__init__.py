import os
import pathlib
from tempfile import SpooledTemporaryFile

from web.core.decorators import as_annotated_dependency
from web.core.settings import settings
from web.logger import _log
from web.services.file.exceptions import (
    RootDirectoryNotFoundException,
    TestcaseFileNotFoundException,
    TestcaseFileTooLargeException,
)


@as_annotated_dependency
class FileService:
    TEST_CASE_FILE_SIZE_LIMIT = 8 * 1024 * 1024

    def __init__(self) -> None:
        self.root_path = pathlib.Path(settings.judge_file_path)

    def write_testcase_file(
        self,
        problem_id: int,
        testcase_id: int,
        input_file: SpooledTemporaryFile[bytes],
        output_file: SpooledTemporaryFile[bytes],
    ):
        if not self.root_path.exists():
            raise RootDirectoryNotFoundException()

        testcase_path = self.root_path / f"{problem_id}" / "testcases"
        testcase_path.mkdir(parents=True, exist_ok=True)

        input_size = self._format_and_write_testcase(
            input_file, testcase_path / f"{testcase_id}.in"
        )
        output_size = self._format_and_write_testcase(
            output_file, testcase_path / f"{testcase_id}.out"
        )

        if (is_input_large := input_size > self.TEST_CASE_FILE_SIZE_LIMIT) or (
            is_output_large := output_size > self.TEST_CASE_FILE_SIZE_LIMIT
        ):
            self.delete_testcase_file(problem_id, testcase_id)
            raise TestcaseFileTooLargeException(is_input_large, is_output_large)

        return input_size, output_size

    def _format_and_write_testcase(
        self, temp_file: SpooledTemporaryFile[bytes], file: pathlib.Path
    ) -> int:
        with open(file, "wb") as f:
            temp_file.seek(0)
            content = temp_file.readlines()
            size = 0

            for line in content:
                strip = line.strip()

                if len(strip) != 0:
                    f.write(strip)
                    f.write(b"\n")

                    size += len(strip) + 1

        return size

    def read_testcase_file(self, problem_id: int, testcase_id: int):
        testcase_input_file = (
            self.root_path / f"{problem_id}" / "testcases" / f"{testcase_id}.in"
        )
        testcase_output_file = (
            self.root_path / f"{problem_id}" / "testcases" / f"{testcase_id}.out"
        )

        if not (testcase_input_file.exists() or testcase_output_file.exists()):
            raise TestcaseFileNotFoundException()

        with open(testcase_input_file) as f:
            input = f.read()

        with open(testcase_output_file) as f:
            output = f.read()

        return (input, output)

    def delete_testcase_file(self, problem_id: int, testcase_id: int):
        input_file = (
            self.root_path / f"{problem_id}" / "testcases" / f"{testcase_id}.in"
        )
        output_file = (
            self.root_path / f"{problem_id}" / "testcases" / f"{testcase_id}.in"
        )

        try:
            if os.path.exists(input_file):
                os.remove(input_file)

            if os.path.exists(output_file):
                os.remove(output_file)
        except Exception as e:
            _log.warn("Delete testcase failed.", exc_info=e)
