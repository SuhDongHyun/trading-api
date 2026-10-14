"""KIS appkey 한도를 위해 컨테이너 Singleton 하나를 프로세스에서 공유한다.

초당 10건 창만으로는 순간 요청 몰림을 막지 못하므로 최소 150ms 간격도 적용한다.
"""

from pyrate_limiter import Duration, Limiter, Rate

from common.min_interval_throttle import MinIntervalThrottle

KIS_API_CALLS_PER_SECOND = 10
KIS_API_MIN_INTERVAL_SECONDS = 0.15
KIS_API_RATE_LIMIT_KEY = "kis-rest-api"


class KisRateLimiter:
    """프로세스의 KIS 호출자가 함께 쓰는 rate limiter."""

    def __init__(
        self,
        limiter: Limiter | None = None,
        min_interval_throttle: MinIntervalThrottle | None = None,
    ):
        self._limiter = limiter or Limiter(
            Rate(KIS_API_CALLS_PER_SECOND, Duration.SECOND)
        )
        self._min_interval_throttle = min_interval_throttle or MinIntervalThrottle(
            KIS_API_MIN_INTERVAL_SECONDS
        )

    def acquire(self) -> None:
        """초당 제한과 150ms 간격을 모두 만족할 때까지 블로킹한다."""

        self._limiter.try_acquire(KIS_API_RATE_LIMIT_KEY, blocking=True)
        self._min_interval_throttle.acquire()
