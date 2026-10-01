from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from notifications.dependencies import get_notification_service
from notifications.schemas import (
    NotificationCreatedResponse,
    NotificationRequest,
    NotificationStatusResponse,
)
from notifications.service import (
    NotificationNotFound,
    NotificationNotProcessable,
    NotificationService,
)

router = APIRouter(prefix="/requests", tags=["Notifications Requests"])

Service = Annotated[NotificationService, Depends(get_notification_service)]


async def notification_not_found_handler(
    request: Request, exc: NotificationNotFound
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": f"Request {exc.request_id} not found"},
    )


async def notification_not_processable_handler(
    request: Request, exc: NotificationNotProcessable
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": f"Request {exc.request_id} is not processable"},
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_request(
    body: NotificationRequest, service: Service
) -> NotificationCreatedResponse:
    notification = service.create(body.to, body.message, body.type)
    return NotificationCreatedResponse(id=notification.id)


@router.post(
    "/{request_id}/process",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Request not found"},
        status.HTTP_409_CONFLICT: {"description": "Request is not processable"},
    },
)
def process_request(request_id: str, service: Service) -> None:
    service.process(request_id)


@router.get(
    "/{request_id}",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Request not found"}},
)
async def get_request(request_id: str, service: Service) -> NotificationStatusResponse:
    notification = service.get(request_id)
    return NotificationStatusResponse(id=notification.id, status=notification.status)
