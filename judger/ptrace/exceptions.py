from judger.ptrace.constants import PtraceRequest


class PtraceException(Exception):
    def __init__(self, request: PtraceRequest) -> None:
        super().__init__(f"Exception occured during ptrace request {request}.")
        self.request = request
