import unittest

from stock.domain.adapter.api_client import IApiClient
from stock.domain.market import OverseasMarketIndexPrice
from stock.service.market_index_service import MarketIndexService


class FakeMarketClient:
    """시장 지수 서비스 테스트용 market client."""

    def __init__(self):
        """호출 인자를 기록할 목록을 초기화한다."""

        self.calls = []

    def get_treasury_yield(self, code, start_date, end_date):
        """시장 지수 조회 호출 인자를 기록하고 고정 결과를 반환한다."""

        self.calls.append(("get_treasury_yield", code, start_date, end_date))
        return [
            OverseasMarketIndexPrice(
                date="20260105",
                open_price=3.1,
                high_price=3.2,
                low_price=3.0,
                close_price=3.15,
            )
        ]

    def get_sp500_index(self, start_date, end_date):
        """S&P 500 조회 호출 인자를 기록하고 고정 결과를 반환한다."""

        self.calls.append(("get_sp500_index", start_date, end_date))
        return [
            OverseasMarketIndexPrice(
                date="20260105",
                open_price=3.1,
                high_price=3.2,
                low_price=3.0,
                close_price=3.15,
            )
        ]


class MarketIndexServiceTest(unittest.TestCase):
    """시장 지수 서비스 동작을 검증한다."""

    def test_service_delegates_treasury_yield_query_by_country_and_maturity(self):
        """국가와 만기로 국채 수익률 지수 코드를 선택해 market client로 위임한다."""

        market_client = FakeMarketClient()
        service = MarketIndexService(market_client)

        result = service.get_korea_3y_treasury_yield(
            start_date="20260105",
            end_date="20260107",
        )

        self.assertEqual(
            market_client.calls,
            [("get_treasury_yield", "Y0101", "20260105", "20260107")],
        )
        self.assertEqual(result[0].close_price, 3.15)

    def test_service_delegates_sp500_index_query(self):
        """S&P 500 지수 조회를 market client로 위임한다."""

        market_client = FakeMarketClient()
        service = MarketIndexService(market_client)

        result = service.get_sp500_index(
            start_date="20260105",
            end_date="20260107",
        )

        self.assertEqual(
            market_client.calls,
            [("get_sp500_index", "20260105", "20260107")],
        )
        self.assertEqual(result[0].close_price, 3.15)

    def test_api_client_contract_includes_market_index_price_query(self):
        """시장 지수 가격 조회가 API client 포트 계약에 포함되어야 한다."""

        self.assertIn(
            "get_overseas_market_index_prices",
            IApiClient.__abstractmethods__,
        )
        self.assertIn(
            "get_domestic_market_index_prices",
            IApiClient.__abstractmethods__,
        )


if __name__ == "__main__":
    unittest.main()
