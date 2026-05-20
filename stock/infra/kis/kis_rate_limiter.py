"""한국투자증권 REST API 호출량을 제한하는 공통 limiter."""

from pyrate_limiter import Duration, Limiter, Rate

KIS_API_CALLS_PER_SECOND = 10
KIS_API_RATE_LIMIT_KEY = "kis-rest-api"

_limiter = Limiter(Rate(KIS_API_CALLS_PER_SECOND, Duration.SECOND))


def acquire_kis_api_slot() -> None:
    """초당 10건 제한 안에서 KIS API 호출 가능 슬롯이 생길 때까지 대기한다."""

    _limiter.try_acquire(KIS_API_RATE_LIMIT_KEY, blocking=True)
