from pydantic import BaseModel

from notifications.models import NotificationType, NotificationStatus


class NotificationRequest(BaseModel):
    to: str
    message: str
    type: NotificationType


class NotificationCreatedResponse(BaseModel):
    id: str


class NotificationStatusResponse(BaseModel):
    id: str
    status: NotificationStatus
