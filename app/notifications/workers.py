import asyncio
import logging

from notifications.queue import DeliveryQueue
from notifications.service import NotificationService

logger = logging.getLogger(__name__)


class DeliveryWorkers:
    def __init__(
        self, service: NotificationService, queue: DeliveryQueue, count: int
    ) -> None:
        self._service = service
        self._queue = queue
        self._count = count
        self._tasks: list[asyncio.Task] = []

    def start(self) -> None:
        for _ in range(self._count):
            self._tasks.append(asyncio.create_task(self._run()))

    async def _run(self) -> None:
        while True:
            request_id = await self._queue.get()
            try:
                await self._service.deliver(request_id)
            except Exception:
                logger.exception("Error delivering notification %s", request_id)
            finally:
                self._queue.task_done()

    async def stop(self) -> None:
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
