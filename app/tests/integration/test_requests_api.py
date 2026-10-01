import httpx
import pytest

from main import app
from notifications.dependencies import get_notification_service
from notifications.models import NotificationStatus
from notifications.repository import NotificationRepository
from notifications.service import NotificationService

pytestmark = pytest.mark.anyio

VALID_BODY = {"to": "user@example.com", "message": "hola", "type": "email"}


@pytest.fixture
def repository():
    repository = NotificationRepository()
    app.dependency_overrides[get_notification_service] = lambda: NotificationService(repository)
    yield repository
    app.dependency_overrides.clear()


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_create_request_returns_201_with_id_and_stores_it_queued(client, repository):
    response = await client.post("/v1/requests", json=VALID_BODY)

    assert response.status_code == 201
    notification = repository.get(response.json()["id"])
    assert notification is not None
    assert notification.status == NotificationStatus.QUEUED


@pytest.mark.parametrize(
    "body",
    [
        {**VALID_BODY, "type": "fax"},
        {"message": "hola", "type": "email"},
        {"to": "user@example.com", "type": "email"},
    ],
)
async def test_create_request_rejects_invalid_body_with_422(client, repository, body):
    response = await client.post("/v1/requests", json=body)

    assert response.status_code == 422
