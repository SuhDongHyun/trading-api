"""프로세스 안의 외부 API 요청 사이 최소 간격을 보장한다."""

from threading import Lock
from time import monotonic, sleep
from typing import Callable


class MinIntervalThrottle:
    """동시 호출을 직렬화하고 요청 슬롯 사이 최소 간격을 적용한다."""

    def __init__(
        self,
        interval_seconds: float,
        clock: Callable[[], float] | None = None,
        wait: Callable[[float], None] | None = None,
    ):
        self._interval_seconds = interval_seconds
        self._clock = clock or monotonic
        self._wait = wait or sleep
        self._lock = Lock()
        self._last_request_at: float | None = None

    def acquire(self) -> None:
        """이전 슬롯과 간격이 부족하면 대기한 뒤 다음 요청 슬롯을 예약한다."""

        with self._lock:
            now = self._clock()
            if self._last_request_at is not None:
                wait_seconds = self._interval_seconds - (
                    now - self._last_request_at
                )
                if wait_seconds > 0:
                    self._wait(wait_seconds)
                    now = self._clock()
            self._last_request_at = now
