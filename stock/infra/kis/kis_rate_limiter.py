"""한국투자증권 REST API 호출량을 제한하는 공통 limiter."""

from threading import Lock
from time import monotonic, sleep

from pyrate_limiter import Duration, Limiter, Rate

KIS_API_CALLS_PER_SECOND = 10
KIS_API_MIN_INTERVAL_SECONDS = 0.15
KIS_API_RATE_LIMIT_KEY = "kis-rest-api"

_limiter = Limiter(Rate(KIS_API_CALLS_PER_SECOND, Duration.SECOND))
_request_interval_lock = Lock()
_last_request_at: float | None = None


def acquire_kis_api_slot() -> None:
    """초당 10건 제한과 요청 간 150ms 간격을 지키며 호출 가능할 때까지 대기한다."""

    _limiter.try_acquire(KIS_API_RATE_LIMIT_KEY, blocking=True)
    with _request_interval_lock:
        global _last_request_at

        now = monotonic()
        if _last_request_at is not None:
            wait_seconds = KIS_API_MIN_INTERVAL_SECONDS - (now - _last_request_at)
            if wait_seconds > 0:
                sleep(wait_seconds)
                now = monotonic()

        _last_request_at = now
