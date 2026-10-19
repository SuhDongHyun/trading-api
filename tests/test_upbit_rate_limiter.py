from time import monotonic

from pyrate_limiter import Duration, Limiter, Rate

from bitcoin.infra.upbit.upbit_rate_limiter import (
    UPBIT_API_CALLS_PER_SECOND,
    UPBIT_RATE_LIMIT_GROUPS,
    UpbitRateLimiter,
)


def test_upbit_rate_limiter_uses_separate_limiters_for_each_group():
    limiters = {
        group: Limiter(Rate(1, Duration.SECOND)) for group in UPBIT_RATE_LIMIT_GROUPS
    }
    rate_limiter = UpbitRateLimiter(limiters=limiters)

    rate_limiter.acquire("market")
    started_at = monotonic()
    rate_limiter.acquire("ticker")
    elapsed = monotonic() - started_at

    assert UPBIT_API_CALLS_PER_SECOND == 10
    assert elapsed < 0.75
