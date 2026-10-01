import pytest

from notifications.models import NotificationStatus
from notifications.repository import NotificationRepository
from notifications.service import NotificationNotFound, NotificationService


def test_create_stores_a_queued_notification():
    repository = NotificationRepository()
    service = NotificationService(repository)

    notification = service.create("user@example.com", "hola", "email")

    assert notification.status == NotificationStatus.QUEUED
    assert notification.to == "user@example.com"
    assert notification.message == "hola"
    assert notification.type == "email"
    assert repository.get(notification.id) is notification


def test_create_assigns_a_different_id_to_each_notification():
    service = NotificationService(NotificationRepository())

    first = service.create("user@example.com", "hola", "email")
    second = service.create("user@example.com", "hola", "email")

    assert first.id != second.id


def test_get_returns_the_stored_notification():
    service = NotificationService(NotificationRepository())
    created = service.create("user@example.com", "hola", "email")

    assert service.get(created.id) is created


def test_get_raises_not_found_for_unknown_id():
    service = NotificationService(NotificationRepository())

    with pytest.raises(NotificationNotFound) as exc_info:
        service.get("missing")

    assert exc_info.value.request_id == "missing"
