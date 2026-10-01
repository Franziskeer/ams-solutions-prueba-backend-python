import pytest
from notifications.queue import DeliveryQueue


@pytest.mark.anyio
async def test_delivery_queue():
    queue = DeliveryQueue()
    queue.put("a")
    queue.put("b")
    assert await queue.get() == "a"
    assert await queue.get() == "b"
    queue.task_done()
    queue.task_done()
    await queue.join()
