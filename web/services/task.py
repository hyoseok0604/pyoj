from web.core.database import AsyncRedisDependency
from web.core.decorators import as_annotated_dependency
from worker.tasks import parse_systemcalls_task


@as_annotated_dependency
class TaskService:
    def __init__(self, redis: AsyncRedisDependency) -> None:
        self.redis = redis

    def request_parse_systemcall_task(self):
        parse_systemcalls_task.delay()
