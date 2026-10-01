import asyncio

import httpx
import pytest

from main import app
from notifications.dependencies import get_notification_service
from notifications.models import NotificationStatus
from notifications.provider import ProviderClient
from notifications.queue import DeliveryQueue
from notifications.repository import NotificationRepository
from notifications.service import NotificationService
from notifications.workers import DeliveryWorkers

pytestmark = pytest.mark.anyio

VALID_BODY = {"to": "user@example.com", "message": "hola", "type": "email"}


@pytest.fixture
async def api():
    repository = NotificationRepository()
    queue = DeliveryQueue()
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200, json={"status": "delivered", "provider_id": "p-1"}
        )
    )
    service = NotificationService(
        repository, ProviderClient(transport=transport), queue
    )
    workers = DeliveryWorkers(service, queue, count=1)
    app.dependency_overrides[get_notification_service] = lambda: service
    yield repository, queue, workers
    await workers.stop()
    app.dependency_overrides.clear()


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_create_request_returns_201_with_id_and_stores_it_queued(client, api):
    repository, _queue, _workers = api
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
async def test_create_request_rejects_invalid_body_with_422(client, api, body):
    response = await client.post("/v1/requests", json=body)

    assert response.status_code == 422


async def test_get_request_returns_id_and_queued_status(client, api):
    request_id = (await client.post("/v1/requests", json=VALID_BODY)).json()["id"]

    response = await client.get(f"/v1/requests/{request_id}")

    assert response.status_code == 200
    assert response.json() == {"id": request_id, "status": "queued"}


async def test_get_request_returns_404_for_unknown_id(client, api):
    response = await client.get("/v1/requests/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Request missing not found"}


async def test_process_request_returns_202_and_marks_processing_then_sent(client, api):
    repository, queue, workers = api
    request_id = (await client.post("/v1/requests", json=VALID_BODY)).json()["id"]

    process_response = await client.post(f"/v1/requests/{request_id}/process")
    status_after_accept = await client.get(f"/v1/requests/{request_id}")

    assert process_response.status_code == 202
    assert status_after_accept.json() == {"id": request_id, "status": "processing"}

    workers.start()
    await queue.join()
    status_after_delivery = await client.get(f"/v1/requests/{request_id}")

    assert status_after_delivery.json() == {"id": request_id, "status": "sent"}
    assert repository.get(request_id).status == NotificationStatus.SENT


async def test_process_request_returns_404_for_unknown_id(client, api):
    response = await client.post("/v1/requests/missing/process")

    assert response.status_code == 404
    assert response.json() == {"detail": "Request missing not found"}


async def test_process_request_returns_409_when_not_queued(client, api):
    request_id = (await client.post("/v1/requests", json=VALID_BODY)).json()["id"]
    await client.post(f"/v1/requests/{request_id}/process")

    response = await client.post(f"/v1/requests/{request_id}/process")

    assert response.status_code == 409
    assert response.json() == {"detail": f"Request {request_id} is not processable"}


async def test_concurrent_process_requests_enqueue_only_once(client, api):
    _repository, queue, _workers = api
    request_id = (await client.post("/v1/requests", json=VALID_BODY)).json()["id"]

    responses = await asyncio.gather(
        *(client.post(f"/v1/requests/{request_id}/process") for _ in range(10))
    )

    assert sorted(r.status_code for r in responses) == [202] + [409] * 9
    assert queue.qsize() == 1
