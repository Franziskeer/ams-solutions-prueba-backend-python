import json

import httpx
import pytest

from config import settings
from notifications.provider import ProviderClient, ProviderError

pytestmark = pytest.mark.anyio


async def notify(handler) -> str:
    client = ProviderClient(transport=httpx.MockTransport(handler))
    try:
        return await client.notify("user@example.com", "hola", "email")
    finally:
        await client.aclose()


async def test_returns_provider_id_on_success():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": "delivered", "provider_id": "p-1234"})

    assert await notify(handler) == "p-1234"


async def test_sends_api_key_and_notification_body():
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json={"status": "delivered", "provider_id": "p-1234"})

    await notify(handler)

    request = captured[0]
    assert request.method == "POST"
    assert request.url == f"{settings.provider_base_url}/v1/notify"
    assert request.headers["X-API-Key"] == settings.provider_api_key
    assert json.loads(request.content) == {
        "to": "user@example.com",
        "message": "hola",
        "type": "email",
    }


@pytest.mark.parametrize("status_code", [401, 429, 500])
async def test_raises_provider_error_with_status_code(status_code: int):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json={"detail": "error"})

    with pytest.raises(ProviderError) as exc_info:
        await notify(handler)

    assert exc_info.value.status_code == status_code


@pytest.mark.parametrize(
    "error",
    [httpx.ConnectError("connection refused"), httpx.ReadTimeout("timed out")],
)
async def test_raises_provider_error_without_status_code_on_transport_error(
    error: httpx.HTTPError,
):
    def handler(request: httpx.Request) -> httpx.Response:
        raise error

    with pytest.raises(ProviderError) as exc_info:
        await notify(handler)

    assert exc_info.value.status_code is None
