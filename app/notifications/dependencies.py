from notifications.repository import NotificationRepository
from notifications.service import NotificationService

_repository = NotificationRepository()


def get_notification_service() -> NotificationService:
    return NotificationService(_repository)
