from config import settings
from notifications.provider import ProviderClient
from notifications.queue import DeliveryQueue
from notifications.rate_limiter import SlidingWindowRateLimiter
from notifications.repository import NotificationRepository
from notifications.service import NotificationService
from notifications.workers import DeliveryWorkers

_limiter = SlidingWindowRateLimiter(
    settings.provider_rate_limit, settings.provider_rate_window
)
_repository = NotificationRepository()
_provider = ProviderClient(rate_limiter=_limiter)
_queue = DeliveryQueue()
_service = NotificationService(_repository, _provider, _queue)
_workers = DeliveryWorkers(_service, _queue, settings.delivery_workers)


def get_notification_service() -> NotificationService:
    return _service


def get_delivery_workers() -> DeliveryWorkers:
    return _workers


def get_provider() -> ProviderClient:
    return _provider
