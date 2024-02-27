import logging
from contextlib import AbstractContextManager
from types import TracebackType

_log = logging.getLogger("web")


class DisableSqlalchemyLogger(AbstractContextManager):
    def __init__(self) -> None:
        self.logger = logging.getLogger("sqlalchemy.engine.Engine")

    def __enter__(self):
        self.handlers = self.logger.handlers
        self.logger.handlers = []
        return self

    def __exit__(
        self,
        __exc_type: type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None,
    ) -> bool | None:
        self.logger.handlers = self.handlers
