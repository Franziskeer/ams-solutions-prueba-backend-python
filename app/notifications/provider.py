import httpx

from config import settings


class ProviderError(Exception):
    def __init__(self, status_code: int | None, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code

    @property
    def retryable(self) -> bool:
        return (
            self.status_code is None
            or self.status_code == 429
            or self.status_code >= 500
        )


class ProviderClient:
    def __init__(
        self,
        timeout: float = 5.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=settings.provider_base_url,
            headers={"X-API-Key": settings.provider_api_key},
            timeout=timeout,
            transport=transport,
        )

    async def notify(self, to: str, message: str, type: str) -> str:
        try:
            response = await self._client.post(
                "/v1/notify",
                json={"to": to, "message": message, "type": type},
            )
        except httpx.HTTPError as exc:
            raise ProviderError(None, str(exc)) from exc

        if response.status_code != httpx.codes.OK:
            raise ProviderError(response.status_code, response.text)

        return response.json()["provider_id"]

    async def aclose(self) -> None:
        await self._client.aclose()
