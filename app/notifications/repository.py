from notifications.models import Notification


class NotificationRepository:
    def __init__(self) -> None:
        self._items: dict[str, Notification] = {}

    def add(self, notification: Notification) -> None:
        self._items[notification.id] = notification

    def get(self, notification_id: str) -> Notification | None:
        return self._items.get(notification_id)
