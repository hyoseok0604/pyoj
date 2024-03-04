import asyncio
from asyncio import Queue
from typing import Callable

from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger
from psycopg import AsyncConnection, Notify, OperationalError

notify_on_testcase_result_update_function = PGFunction.from_sql(
    """CREATE OR REPLACE FUNCTION public.notify_on_testcase_result_update_function() RETURNS TRIGGER AS $$
    DECLARE
        payload json;
        testcase_count INTEGER;
        completed_testcase_count INTEGER;
    BEGIN
        SELECT count(*)
        INTO testcase_count
        FROM submission_testcase_result
        WHERE submission_id = NEW.submission_id;

        SELECT count(*)
        INTO completed_testcase_count
        FROM submission_testcase_result
        WHERE submission_id = NEW.submission_id
        AND result IS NOT NULL;

        payload := json_build_object(
            'submission_id', NEW.submission_id,
            'testcase_id', NEW.testcase_id,
            'result', NEW.result,
            'testcase_count', testcase_count,
            'completed_testcase_count', completed_testcase_count,
            'time', NEW.time,
            'memory', NEW.memory
        );

        PERFORM pg_notify('testcase_result_events', payload::text);

        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;"""  # noqa: E501
)

notify_on_testcase_result_update_trigger = PGTrigger.from_sql(
    """CREATE TRIGGER notify_on_testcase_result_update_trigger
        AFTER UPDATE
        ON submission_testcase_result
        FOR EACH ROW
        EXECUTE PROCEDURE notify_on_testcase_result_update_function();"""
)


class PostgresAsyncNotifyListenerHandler:
    def __init__(self, filter_fn: Callable[[Notify], bool]) -> None:
        self.queue: Queue[Notify] = Queue()
        self.filter_fn = filter_fn
        self.need_remove = False

    async def update_need_remove(self):
        ...


class PostgresAsyncNotifyListener:
    def __init__(self, uri: str) -> None:
        self.uri = uri
        self.handlers: list[PostgresAsyncNotifyListenerHandler] = []

    async def start(self):
        await self.connect()
        await self.listen()

        asyncio.create_task(self.handle_notifies())

    async def connect(self):
        self.connection = await AsyncConnection.connect(
            self.uri, application_name="notify-listen"
        )

    async def listen(self):
        await self.connection.execute("LISTEN testcase_result_events")
        await self.connection.commit()

    async def handle_notifies(self):
        try:
            async for notify in self.connection.notifies():
                for handler in self.handlers:
                    if handler.filter_fn(notify):
                        handler.queue.put_nowait(notify)
                self.handlers = list(
                    filter(lambda handler: not handler.need_remove, self.handlers)
                )
        except OperationalError:
            ...

    def add_handler(self, handler: PostgresAsyncNotifyListenerHandler):
        self.handlers.append(handler)
