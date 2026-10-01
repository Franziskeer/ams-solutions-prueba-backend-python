from pydantic import BaseModel

from notifications.models import NotificationType


class NotificationRequest(BaseModel):
    to: str
    message: str
    type: NotificationType


class NotificationCreatedResponse(BaseModel):
    id: str
