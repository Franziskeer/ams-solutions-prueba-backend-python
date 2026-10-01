from uuid import uuid4

from notifications.models import Notification, NotificationType
from notifications.repository import NotificationRepository


class NotificationService:
    def __init__(self, repository: NotificationRepository) -> None:
        self._repository = repository

    def create(self, to: str, message: str, type: NotificationType) -> Notification:
        notification = Notification(id=str(uuid4()), to=to, message=message, type=type)
        self._repository.add(notification)
        return notification
