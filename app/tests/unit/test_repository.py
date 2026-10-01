from notifications.models import Notification
from notifications.repository import NotificationRepository


def test_get_returns_added_notification():
    repository = NotificationRepository()
    notification = Notification(id="n-1", to="user@example.com", message="hola", type="email")

    repository.add(notification)

    assert repository.get("n-1") is notification


def test_get_returns_none_for_unknown_id():
    assert NotificationRepository().get("missing") is None
