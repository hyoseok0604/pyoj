import asyncio
from asyncio import Queue
from typing import Callable

from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger
from alembic_utils.replaceable_entity import register_entities
from psycopg import AsyncConnection, Notify, OperationalError

from web.logger import _log

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


register_entities(
    [
        notify_on_testcase_result_update_function,
        notify_on_testcase_result_update_trigger,
    ]
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
        asyncio.create_task(self.update_and_remove_handler())

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
        except OperationalError:
            ...

    async def update_and_remove_handler(self):
        while True:
            _log.info(
                f"Start update and remove handlers. Current handler count : {len(self.handlers)}"
            )

            await asyncio.gather(
                *[handler.update_need_remove() for handler in self.handlers]
            )

            self.handlers = list(
                filter(lambda handler: not handler.need_remove, self.handlers)
            )

            _log.info(
                f"Updated handler count : {len(self.handlers)}, sleep 60 seconds."
            )

            await asyncio.sleep(60)

    def add_handler(self, handler: PostgresAsyncNotifyListenerHandler):
        self.handlers.append(handler)
