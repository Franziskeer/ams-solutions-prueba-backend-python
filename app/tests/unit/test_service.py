import httpx
import pytest

from notifications.models import NotificationStatus
from notifications.provider import ProviderClient
from notifications.repository import NotificationRepository
from notifications.service import (
    NotificationNotFound,
    NotificationNotProcessable,
    NotificationService,
)


def _service(
    repository: NotificationRepository | None = None,
    *,
    status_code: int = 200,
    calls: list[httpx.Request] | None = None,
) -> NotificationService:
    def handler(request: httpx.Request) -> httpx.Response:
        if calls is not None:
            calls.append(request)
        if status_code == 200:
            return httpx.Response(
                200, json={"status": "delivered", "provider_id": "p-1"}
            )
        return httpx.Response(status_code, json={"detail": "error"})

    return NotificationService(
        repository or NotificationRepository(),
        ProviderClient(transport=httpx.MockTransport(handler)),
    )


def test_create_stores_a_queued_notification():
    repository = NotificationRepository()
    service = _service(repository)

    notification = service.create("user@example.com", "hola", "email")

    assert notification.status == NotificationStatus.QUEUED
    assert notification.to == "user@example.com"
    assert notification.message == "hola"
    assert notification.type == "email"
    assert repository.get(notification.id) is notification


def test_create_assigns_a_different_id_to_each_notification():
    service = _service()

    first = service.create("user@example.com", "hola", "email")
    second = service.create("user@example.com", "hola", "email")

    assert first.id != second.id


def test_get_returns_the_stored_notification():
    service = _service()
    created = service.create("user@example.com", "hola", "email")

    assert service.get(created.id) is created


def test_get_raises_not_found_for_unknown_id():
    service = _service()

    with pytest.raises(NotificationNotFound) as exc_info:
        service.get("missing")

    assert exc_info.value.request_id == "missing"


@pytest.mark.anyio
async def test_process_marks_notification_as_sent_on_provider_success():
    service = _service()
    created = service.create("user@example.com", "hola", "email")

    processed = await service.process(created.id)

    assert processed.status == NotificationStatus.SENT
    assert service.get(created.id).status == NotificationStatus.SENT


@pytest.mark.anyio
async def test_process_marks_notification_as_failed_on_provider_error():
    service = _service(status_code=500)
    created = service.create("user@example.com", "hola", "email")

    processed = await service.process(created.id)

    assert processed.status == NotificationStatus.FAILED
    assert service.get(created.id).status == NotificationStatus.FAILED


@pytest.mark.anyio
async def test_process_rejects_non_queued_notification_without_calling_provider():
    calls: list[httpx.Request] = []
    service = _service(calls=calls)
    created = service.create("user@example.com", "hola", "email")
    await service.process(created.id)

    with pytest.raises(NotificationNotProcessable) as exc_info:
        await service.process(created.id)

    assert exc_info.value.request_id == created.id
    assert len(calls) == 1
