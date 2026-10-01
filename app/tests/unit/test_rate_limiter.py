import pytest

from notifications.rate_limiter import SlidingWindowRateLimiter

pytestmark = pytest.mark.anyio


class FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


async def test_acquire_allows_up_to_limit_without_waiting():
    clock = FakeClock()
    sleeps: list[float] = []

    async def sleep(seconds: float) -> None:
        sleeps.append(seconds)
        clock.advance(seconds)

    limiter = SlidingWindowRateLimiter(2, 10.0, clock=clock, sleep=sleep)

    await limiter.acquire()
    await limiter.acquire()

    assert sleeps == []


async def test_acquire_waits_when_window_is_full():
    clock = FakeClock()
    sleeps: list[float] = []

    async def sleep(seconds: float) -> None:
        sleeps.append(seconds)
        clock.advance(seconds)

    limiter = SlidingWindowRateLimiter(2, 10.0, clock=clock, sleep=sleep)

    await limiter.acquire()
    clock.advance(1.0)
    await limiter.acquire()
    await limiter.acquire()

    assert len(sleeps) == 1
    assert sleeps[0] == pytest.approx(9.0)


async def test_acquire_allows_calls_again_after_window_slides():
    clock = FakeClock()
    sleeps: list[float] = []

    async def sleep(seconds: float) -> None:
        sleeps.append(seconds)
        clock.advance(seconds)

    limiter = SlidingWindowRateLimiter(1, 10.0, clock=clock, sleep=sleep)

    await limiter.acquire()
    clock.advance(10.0)
    await limiter.acquire()

    assert sleeps == []
