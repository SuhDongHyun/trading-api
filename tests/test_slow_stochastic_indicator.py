import unittest

from stock.domain.price import (
    DailyStockPrice,
    DailyStockPriceResult,
    DailyStockPriceSummary,
)
from stock.interface.controller.stock_quote_controller import get_slow_stochastic
from stock.interface.schema.stock_quote import SlowStochasticRequest
from stock.service.stock_quote_service import StockQuoteService


class FakeApiClient:
    """Slow Stochastic 계산에 사용할 고정 일봉 가격 API 클라이언트."""

    def __init__(self):
        """호출 인자를 기록할 목록을 초기화한다."""

        self.calls = []

    def get_daily_stock_prices(
        self, market, code, start_date, end_date, period, adjusted_price
    ):
        """Slow Stochastic 계산용 일봉 가격을 반환한다."""

        self.calls.append((market, code, start_date, end_date, period, adjusted_price))
        return DailyStockPriceResult(
            summary=DailyStockPriceSummary(name="삼성전자", code="005930"),
            prices=[
                DailyStockPrice(
                    date="20240401",
                    open_price=0.0,
                    high_price=10.0,
                    low_price=5.0,
                    close_price=7.0,
                    accumulated_volume=0,
                    accumulated_trading_value=0.0,
                    price_diff=0.0,
                    price_diff_sign="3",
                    change_flag="N",
                ),
                DailyStockPrice(
                    date="20240402",
                    open_price=0.0,
                    high_price=12.0,
                    low_price=6.0,
                    close_price=11.0,
                    accumulated_volume=0,
                    accumulated_trading_value=0.0,
                    price_diff=0.0,
                    price_diff_sign="3",
                    change_flag="N",
                ),
                DailyStockPrice(
                    date="20240403",
                    open_price=0.0,
                    high_price=15.0,
                    low_price=7.0,
                    close_price=14.0,
                    accumulated_volume=0,
                    accumulated_trading_value=0.0,
                    price_diff=0.0,
                    price_diff_sign="3",
                    change_flag="N",
                ),
                DailyStockPrice(
                    date="20240404",
                    open_price=0.0,
                    high_price=14.0,
                    low_price=8.0,
                    close_price=9.0,
                    accumulated_volume=0,
                    accumulated_trading_value=0.0,
                    price_diff=0.0,
                    price_diff_sign="3",
                    change_flag="N",
                ),
                DailyStockPrice(
                    date="20240405",
                    open_price=0.0,
                    high_price=16.0,
                    low_price=10.0,
                    close_price=15.0,
                    accumulated_volume=0,
                    accumulated_trading_value=0.0,
                    price_diff=0.0,
                    price_diff_sign="3",
                    change_flag="N",
                ),
            ],
        )


class SlowStochasticIndicatorFeatureTest(unittest.TestCase):
    """Slow Stochastic 지표 계산과 controller 응답 변환을 검증한다."""

    def test_service_calculates_slow_stochastic_from_daily_prices(self):
        """서비스가 일봉 가격으로 slow K/D 값을 계산하는지 검증한다."""

        api_client = FakeApiClient()
        service = StockQuoteService(api_client)

        result = service.get_slow_stochastic(
            market="J",
            code="005930",
            start_date="20240401",
            end_date="20240405",
            period="D",
            adjusted_price=True,
            k_period=3,
            k_smoothing_period=2,
            d_period=2,
        )

        self.assertEqual(
            api_client.calls,
            [("J", "005930", "20240401", "20240405", "D", True)],
        )
        self.assertEqual(result.summary.code, "005930")
        self.assertEqual(len(result.values), 1)
        self.assertEqual(result.values[0].date, "20240405")
        self.assertAlmostEqual(result.values[0].slow_k, 61.1111, places=4)
        self.assertAlmostEqual(result.values[0].slow_d, 61.3889, places=4)

    def test_controller_returns_slow_stochastic_response_schema(self):
        """Controller가 Slow Stochastic 결과를 응답 스키마로 변환하는지 검증한다."""

        request = SlowStochasticRequest(
            market="J",
            code="005930",
            start_date="20240401",
            end_date="20240405",
            period="D",
            adjusted_price=True,
            k_period=3,
            k_smoothing_period=2,
            d_period=2,
        )
        service = StockQuoteService(FakeApiClient())

        response = get_slow_stochastic(request, stock_quote_service=service)

        self.assertEqual(response.summary.name, "삼성전자")
        self.assertEqual(response.values[0].date, "20240405")
        self.assertAlmostEqual(response.values[0].slow_k, 61.1111, places=4)
        self.assertAlmostEqual(response.values[0].slow_d, 61.3889, places=4)


if __name__ == "__main__":
    unittest.main()
