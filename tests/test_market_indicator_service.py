import unittest

from stock.domain.adapter.api_client import IApiClient
from stock.domain.market import OverseasMarketIndicatorPrice
from stock.service.market_indicator_service import MarketIndicatorService


class FakeMarketClient:
    """시장 지표 서비스 테스트용 market client."""


class FakeApiClient:
    """시장 지표 서비스 테스트용 API client."""

    def __init__(self):
        """호출 인자를 기록할 목록을 초기화한다."""

        self.calls = []

    def get_overseas_market_indicator_prices(
        self, market, code, start_date, end_date, period
    ):
        """시장 지표 조회 호출 인자를 기록하고 고정 결과를 반환한다."""

        self.calls.append((market, code, start_date, end_date, period))
        return [
            OverseasMarketIndicatorPrice(
                date="20260105",
                open_price=3.1,
                high_price=3.2,
                low_price=3.0,
                close_price=3.15,
            )
        ]


class MarketIndicatorServiceTest(unittest.TestCase):
    """시장 지표 서비스 동작을 검증한다."""

    def test_service_delegates_treasury_yield_query_by_country_and_maturity(self):
        """국가와 만기로 국채 수익률 지표 코드를 선택해 API client로 위임한다."""

        api_client = FakeApiClient()
        service = MarketIndicatorService(FakeMarketClient(), api_client)

        result = service.get_treasury_yield(
            country="KR",
            maturity="3Y",
            start_date="20260105",
            end_date="20260107",
        )

        self.assertEqual(
            api_client.calls,
            [("I", "Y0101", "20260105", "20260107", "D")],
        )
        self.assertEqual(result[0].close_price, 3.15)

    def test_service_delegates_sp500_index_query(self):
        """S&P 500 지표 코드를 선택해 API client로 위임한다."""

        api_client = FakeApiClient()
        service = MarketIndicatorService(FakeMarketClient(), api_client)

        result = service.get_sp500_index(
            start_date="20260105",
            end_date="20260107",
        )

        self.assertEqual(
            api_client.calls,
            [("N", "SPX", "20260105", "20260107", "D")],
        )
        self.assertEqual(result[0].close_price, 3.15)

    def test_api_client_contract_includes_market_indicator_price_query(self):
        """시장 지표 가격 조회가 API client 포트 계약에 포함되어야 한다."""

        self.assertIn(
            "get_overseas_market_indicator_prices",
            IApiClient.__abstractmethods__,
        )


if __name__ == "__main__":
    unittest.main()
