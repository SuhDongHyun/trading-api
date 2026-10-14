"""KIS appkey 한도를 위해 컨테이너 Singleton 하나를 프로세스에서 공유한다.

초당 10건 창만으로는 순간 요청 몰림을 막지 못하므로 최소 150ms 간격도 적용한다.
"""

from threading import Lock
from time import monotonic, sleep
from typing import Callable

from pyrate_limiter import Duration, Limiter, Rate

KIS_API_CALLS_PER_SECOND = 10
KIS_API_MIN_INTERVAL_SECONDS = 0.15
KIS_API_RATE_LIMIT_KEY = "kis-rest-api"


class KisRateLimiter:
    """프로세스의 KIS 호출자가 함께 쓰는 rate limiter."""

    def __init__(
        self,
        limiter: Limiter | None = None,
        clock: Callable[[], float] | None = None,
        wait: Callable[[float], None] | None = None,
    ):
        self._limiter = limiter or Limiter(
            Rate(KIS_API_CALLS_PER_SECOND, Duration.SECOND)
        )
        self._clock = clock or monotonic
        self._wait = wait or sleep
        self._request_interval_lock = Lock()
        self._last_request_at: float | None = None

    def acquire(self) -> None:
        """초당 제한과 150ms 간격을 모두 만족할 때까지 블로킹한다."""

        self._limiter.try_acquire(KIS_API_RATE_LIMIT_KEY, blocking=True)
        with self._request_interval_lock:
            now = self._clock()
            if self._last_request_at is not None:
                wait_seconds = KIS_API_MIN_INTERVAL_SECONDS - (
                    now - self._last_request_at
                )
                if wait_seconds > 0:
                    self._wait(wait_seconds)
                    now = self._clock()

            self._last_request_at = now
