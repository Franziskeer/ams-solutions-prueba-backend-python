import asyncio
import time
from collections import deque
from collections.abc import Awaitable, Callable
from typing import Protocol


class RateLimiter(Protocol):
    async def acquire(self) -> None: ...


class SlidingWindowRateLimiter:
    """Allows at most `limit` acquires within any trailing `window_seconds` interval.

    When the window is full, `acquire` waits until the oldest call falls out of the
    window instead of failing immediately. Matches the provider's sliding-window
    rate limit so clients throttle before causing 429s.
    """

    def __init__(
        self,
        limit: int,
        window_seconds: float,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        self._limit = limit
        self._window_seconds = window_seconds
        self._clock = clock
        self._sleep = sleep
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        while True:
            async with self._lock:
                now = self._clock()
                cutoff = now - self._window_seconds
                while self._timestamps and self._timestamps[0] <= cutoff:
                    self._timestamps.popleft()

                if len(self._timestamps) < self._limit:
                    self._timestamps.append(now)
                    return

                wait_for = self._timestamps[0] + self._window_seconds - now

            await self._sleep(max(wait_for, 0))
