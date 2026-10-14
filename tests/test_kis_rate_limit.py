import unittest
from unittest.mock import Mock

from common.min_interval_throttle import MinIntervalThrottle
from config import KISSetting
from stock.infra.kis.kis_http_client import KisHttpClient
from stock.infra.kis.kis_rate_limiter import (
    KIS_API_CALLS_PER_SECOND,
    KIS_API_MIN_INTERVAL_SECONDS,
    KIS_API_RATE_LIMIT_KEY,
    KisRateLimiter,
)


class FakeLimiter:
    def __init__(self):
        self.try_acquire = Mock()


class FakeResponse:
    status_code = 200
    url = "https://example.test/uapi/test"
    text = "{}"

    def raise_for_status(self):
        return None

    def json(self):
        return {"rt_cd": "0"}


def make_http_client(rate_limiter, get=None):
    return KisHttpClient(
        kis_settings=KISSetting(
            base_url="https://example.test",
            account_num="12345678",
            account_code="01",
            appkey="test-key",
            appsecret="test-secret",
        ),
        token_manager=Mock(auth_headers=Mock(return_value={"authorization": "test"})),
        rate_limiter=rate_limiter,
        get=get or Mock(return_value=FakeResponse()),
    )


class KISRateLimitTest(unittest.TestCase):
    """KIS 호출 제한 상태가 limiter 인스턴스 안에서 유지되는지 검증한다."""

    def test_kis_rate_limiter_uses_ten_calls_per_second(self):
        self.assertEqual(KIS_API_CALLS_PER_SECOND, 10)

    def test_kis_rate_limiter_blocks_until_slot_is_available(self):
        limiter = FakeLimiter()
        throttle = Mock(spec=MinIntervalThrottle)
        rate_limiter = KisRateLimiter(
            limiter=limiter, min_interval_throttle=throttle
        )

        rate_limiter.acquire()

        limiter.try_acquire.assert_called_once_with(
            KIS_API_RATE_LIMIT_KEY, blocking=True
        )
        throttle.acquire.assert_called_once_with()

    def test_kis_rate_limiter_configures_a_150ms_minimum_interval(self):
        self.assertEqual(KIS_API_MIN_INTERVAL_SECONDS, 0.15)

    def test_http_get_waits_for_rate_limit_slot_before_request(self):
        rate_limiter = Mock()
        get = Mock(return_value=FakeResponse())
        http_client = make_http_client(rate_limiter, get=get)

        http_client.get(path="/uapi/test", params={"code": "005930"}, tr_id="TEST")

        rate_limiter.acquire.assert_called_once_with()
        get.assert_called_once()


if __name__ == "__main__":
    unittest.main()
