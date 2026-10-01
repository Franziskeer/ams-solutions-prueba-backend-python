from uuid import uuid4

from notifications.models import Notification, NotificationType
from notifications.repository import NotificationRepository


class NotificationNotFound(Exception):
    def __init__(self, request_id: str) -> None:
        super().__init__(f"Notification with id {request_id} not found")
        self.request_id = request_id


class NotificationService:
    def __init__(self, repository: NotificationRepository) -> None:
        self._repository = repository

    def create(self, to: str, message: str, type: NotificationType) -> Notification:
        notification = Notification(id=str(uuid4()), to=to, message=message, type=type)
        self._repository.add(notification)
        return notification

    def get(self, request_id: str) -> Notification:
        notification = self._repository.get(request_id)
        if notification is None:
            raise NotificationNotFound(request_id=request_id)
        return notification
