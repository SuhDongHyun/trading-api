import unittest
from unittest.mock import patch

from stock.infra.kis.kis_http_client import api_get, api_post
from stock.infra.kis import kis_rate_limiter


class FakeResponse:
    """HTTP 응답 객체의 raise_for_status 동작만 흉내낸다."""

    def raise_for_status(self):
        """테스트용 응답은 항상 성공으로 처리한다."""


class KISRateLimitTest(unittest.TestCase):
    """KIS REST API 호출 제한 적용을 검증한다."""

    def test_kis_rate_limiter_uses_ten_calls_per_second(self):
        """KIS API limiter는 초당 10건 제한을 사용한다."""

        self.assertEqual(kis_rate_limiter.KIS_API_CALLS_PER_SECOND, 10)

    @patch.object(kis_rate_limiter, "_limiter")
    def test_kis_rate_limiter_blocks_until_slot_is_available(self, limiter):
        """제한 초과 시 실패하지 않고 호출 가능할 때까지 대기한다."""

        kis_rate_limiter.acquire_kis_api_slot()

        limiter.try_acquire.assert_called_once_with(
            kis_rate_limiter.KIS_API_RATE_LIMIT_KEY,
            blocking=True,
        )

    @patch("stock.infra.kis.kis_http_client.acquire_kis_api_slot", create=True)
    @patch("stock.infra.kis.kis_http_client.build_header")
    @patch("stock.infra.kis.kis_http_client.get")
    def test_api_get_waits_for_rate_limit_slot_before_request(
        self, get, build_header, acquire
    ):
        """GET 호출 전에 KIS API rate limiter를 통과해야 한다."""

        get.return_value = FakeResponse()
        build_header.return_value = {"authorization": "Bearer token"}

        api_get(path="/uapi/test", params={"code": "005930"}, tr_id="TEST")

        acquire.assert_called_once_with()
        get.assert_called_once()

    @patch("stock.infra.kis.kis_http_client.acquire_kis_api_slot", create=True)
    @patch("stock.infra.kis.kis_http_client.build_header")
    @patch("stock.infra.kis.kis_http_client.post")
    def test_api_post_waits_for_same_rate_limit_slot_before_request(
        self, post, build_header, acquire
    ):
        """POST 호출도 GET과 같은 KIS API rate limiter를 통과해야 한다."""

        post.return_value = FakeResponse()
        build_header.return_value = {"authorization": "Bearer token"}

        api_post(path="/uapi/test", body={"code": "005930"}, tr_id="TEST")

        acquire.assert_called_once_with()
        post.assert_called_once()


if __name__ == "__main__":
    unittest.main()
