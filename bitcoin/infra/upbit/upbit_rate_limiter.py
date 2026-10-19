"""Upbit Quotation REST rate limits are shared by endpoint group and IP."""

from pyrate_limiter import Duration, Limiter, Rate

UPBIT_API_CALLS_PER_SECOND = 10
UPBIT_RATE_LIMIT_GROUPS = ("market", "candle", "trade", "ticker", "orderbook")


class UpbitRateLimiter:
    """프로세스 내에서 Upbit 그룹별 초당 10회 제한을 공유한다."""

    def __init__(self, limiters: dict[str, Limiter] | None = None):
        self._limiters = limiters or {
            group: Limiter(Rate(UPBIT_API_CALLS_PER_SECOND, Duration.SECOND))
            for group in UPBIT_RATE_LIMIT_GROUPS
        }

    def acquire(self, group: str) -> None:
        """지정 그룹의 호출 가능 횟수를 확보할 때까지 대기한다."""

        self._limiters[group].try_acquire("upbit", blocking=True)
