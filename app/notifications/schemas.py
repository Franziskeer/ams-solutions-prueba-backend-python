from pydantic import BaseModel

from notifications.models import NotificationType


class NotificationRequest(BaseModel):
    to: str
    message: str
    type: NotificationType


class NotificationCreated(BaseModel):
    id: str
