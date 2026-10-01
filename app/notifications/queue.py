import asyncio


class DeliveryQueue:
    def __init__(self) -> None:
        self._queue: asyncio.Queue[str] = asyncio.Queue()

    def put(self, request_id: str) -> None:
        self._queue.put_nowait(request_id)

    async def get(self) -> str:
        return await self._queue.get()

    async def join(self) -> None:
        await self._queue.join()

    def task_done(self) -> None:
        self._queue.task_done()
