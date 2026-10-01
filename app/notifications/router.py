from typing import Annotated

from fastapi import APIRouter, Depends, status

from notifications.dependencies import get_notification_service
from notifications.schemas import NotificationCreated, NotificationRequest
from notifications.service import NotificationService

router = APIRouter(prefix="/requests", tags=["Notifications Requests"])

Service = Annotated[NotificationService, Depends(get_notification_service)]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_request(body: NotificationRequest, service: Service) -> NotificationCreated:
    notification = service.create(body.to, body.message, body.type)
    return NotificationCreated(id=notification.id)


@router.post("/{request_id}/process", status_code=status.HTTP_202_ACCEPTED)
async def process_request(request_id: str) -> dict:
    return {}


@router.get("/{request_id}")
async def get_request(request_id: str) -> dict:
    return {}
