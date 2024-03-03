import asyncio
import json

from fastapi import APIRouter, HTTPException, Query, Request, status
from psycopg import Notify
from sse_starlette import EventSourceResponse, ServerSentEvent

from web.core.dependencies import SessionUserDependency
from web.core.pg_notify_listen import (
    PostgresAsyncNotifyListener,
    PostgresAsyncNotifyListenerHandler,
)
from web.schemas.submission import (
    CreateSubmissionRequestSchema,
    CreateSubmissionResponseSchema,
    CreateSubmissionSchema,
)
from web.services.submission import SubmissionService

api_router = APIRouter(prefix="/submissions")


@api_router.post(
    "",
    response_model=CreateSubmissionResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_submission_api(
    schema: CreateSubmissionRequestSchema,
    submission_service: SubmissionService,
    session_user: SessionUserDependency,
):
    if session_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    service_schema = CreateSubmissionSchema(
        **schema.model_dump(), creator_id=session_user.user_id
    )

    submission = await submission_service.create_submission(service_schema)

    return submission


@api_router.get("/events")
async def submissions_events_api(request: Request, id: int = Query()):
    pg_notify_listener: PostgresAsyncNotifyListener = (
        request.app.state.pg_notify_listener
    )

    async def sse_generator():
        def filter_fn(notify: Notify):
            payload = json.loads(notify.payload)

            return payload.get("submission_id", -1) == id

        handler = PostgresAsyncNotifyListenerHandler(filter_fn)

        pg_notify_listener.add_handler(handler)

        try:
            while True:
                notify = await handler.queue.get()

                sse_payload = ServerSentEvent(notify.payload)

                yield sse_payload
        except asyncio.CancelledError:
            handler.need_remove = True

    return EventSourceResponse(sse_generator())
