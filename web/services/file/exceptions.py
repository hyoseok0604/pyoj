from web.services.exceptions import FileTooLargeException, InternalServerException


class RootDirectoryNotFoundException(InternalServerException):
    message = {"_details": "파일 저장을 위한 폴더가 존재하지 않습니다."}


class TestcaseFileNotFoundException(InternalServerException):
    message = {"_details": "테스트 케이스 파일이 존재하지 않습니다."}


class TestcaseFileTooLargeException(FileTooLargeException):
    def __init__(self, input: bool, output: bool) -> None:
        messages = {}

        if input:
            messages.update({"input": "입력 파일의 크기가 너무 큽니다."})
        if output:
            messages.update({"output": "출력 파일의 크기가 너무 큽니다."})
