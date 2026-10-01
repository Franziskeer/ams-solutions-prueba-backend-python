from notifications.provider import ProviderClient
from notifications.repository import NotificationRepository
from notifications.service import NotificationService

_repository = NotificationRepository()
_provider = ProviderClient()


def get_notification_service() -> NotificationService:
    return NotificationService(_repository, _provider)
