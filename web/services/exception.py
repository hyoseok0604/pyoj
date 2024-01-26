class ServiceException(Exception):
    def __init__(self, messages: dict[str, str]) -> None:
        self.messages = messages
