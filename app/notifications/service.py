from uuid import uuid4

from config import settings
from notifications.queue import DeliveryQueue
from notifications.models import Notification, NotificationStatus, NotificationType
from notifications.provider import ProviderClient, ProviderError
from notifications.repository import NotificationRepository
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)


class NotificationNotFound(Exception):
    def __init__(self, request_id: str) -> None:
        super().__init__(f"Notification with id {request_id} not found")
        self.request_id = request_id


class NotificationNotProcessable(Exception):
    def __init__(self, request_id: str) -> None:
        super().__init__(f"Notification with id {request_id} not processable")
        self.request_id = request_id


class NotificationService:
    def __init__(
        self,
        repository: NotificationRepository,
        provider: ProviderClient,
        queue: DeliveryQueue,
        *,
        retrying: AsyncRetrying | None = None,
    ) -> None:
        self._repository = repository
        self._provider = provider
        self._queue = queue
        self._retrying = retrying or AsyncRetrying(
            retry=retry_if_exception(
                lambda e: isinstance(e, ProviderError) and e.retryable
            ),
            stop=stop_after_attempt(settings.retry_attempts),
            wait=wait_exponential_jitter(
                initial=settings.retry_wait_initial, max=settings.retry_wait_max
            ),
            reraise=True,
        )

    def create(self, to: str, message: str, type: NotificationType) -> Notification:
        notification = Notification(id=str(uuid4()), to=to, message=message, type=type)
        self._repository.add(notification)
        return notification

    def get(self, request_id: str) -> Notification:
        notification = self._repository.get(request_id)
        if notification is None:
            raise NotificationNotFound(request_id=request_id)
        return notification

    def accept(self, request_id: str) -> Notification:
        notification = self.get(request_id)
        if notification.status != NotificationStatus.QUEUED:
            raise NotificationNotProcessable(request_id=request_id)
        notification.status = NotificationStatus.PROCESSING
        return notification

    async def deliver(self, request_id: str) -> Notification:
        notification = self.get(request_id)
        try:
            async for attempt in self._retrying:
                with attempt:
                    await self._provider.notify(
                        notification.to, notification.message, notification.type
                    )
            notification.status = NotificationStatus.SENT
        except ProviderError:
            notification.status = NotificationStatus.FAILED
        return notification

    def process(self, request_id: str) -> Notification:
        notification = self.accept(request_id)
        self._queue.put(notification.id)
        return notification
