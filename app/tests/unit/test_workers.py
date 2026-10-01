import httpx
import pytest
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_none,
)

from config import settings
from notifications.models import NotificationStatus
from notifications.provider import ProviderClient, ProviderError
from notifications.queue import DeliveryQueue
from notifications.repository import NotificationRepository
from notifications.service import NotificationService
from notifications.workers import DeliveryWorkers

pytestmark = pytest.mark.anyio


def _service(
    repository: NotificationRepository | None = None,
    queue: DeliveryQueue | None = None,
    *,
    status_code: int = 200,
) -> NotificationService:
    def handler(request: httpx.Request) -> httpx.Response:
        if status_code == 200:
            return httpx.Response(
                200, json={"status": "delivered", "provider_id": "p-1"}
            )
        return httpx.Response(status_code, json={"detail": "error"})

    return NotificationService(
        repository or NotificationRepository(),
        ProviderClient(transport=httpx.MockTransport(handler)),
        queue or DeliveryQueue(),
        retrying=AsyncRetrying(
            retry=retry_if_exception(
                lambda e: isinstance(e, ProviderError) and e.retryable
            ),
            stop=stop_after_attempt(settings.retry_attempts),
            wait=wait_none(),
            reraise=True,
        ),
    )


async def test_workers_deliver_queued_requests():
    repository = NotificationRepository()
    queue = DeliveryQueue()
    service = _service(repository, queue)
    workers = DeliveryWorkers(service, queue, count=2)

    first = service.create("user@example.com", "hola", "email")
    second = service.create("user@example.com", "hola", "email")
    service.accept(first.id)
    service.accept(second.id)
    queue.put(first.id)
    queue.put(second.id)

    workers.start()
    await queue.join()
    await workers.stop()

    assert repository.get(first.id).status == NotificationStatus.SENT
    assert repository.get(second.id).status == NotificationStatus.SENT


async def test_workers_keep_running_after_provider_error():
    repository = NotificationRepository()
    queue = DeliveryQueue()
    service = _service(repository, queue, status_code=500)
    workers = DeliveryWorkers(service, queue, count=1)

    first = service.create("user@example.com", "hola", "email")
    second = service.create("user@example.com", "hola", "email")
    service.accept(first.id)
    service.accept(second.id)
    queue.put(first.id)
    queue.put(second.id)

    workers.start()
    await queue.join()
    await workers.stop()

    assert repository.get(first.id).status == NotificationStatus.FAILED
    assert repository.get(second.id).status == NotificationStatus.FAILED
