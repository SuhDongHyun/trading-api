import unittest

from stock.domain.price import (
    DailyStockPrice,
    DailyStockPriceResult,
    DailyStockPriceSummary,
)
from stock.interface.controller.stock_quote_controller import get_moving_average
from stock.interface.schema.stock_quote import MovingAverageRequest
from stock.service.stock_quote_service import StockQuoteService


class FakeApiClient:
    """이동평균 계산에 사용할 고정 일봉 가격 API 클라이언트."""

    def __init__(self):
        """호출 인자를 기록할 목록을 초기화한다."""

        self.calls = []

    def get_daily_stock_prices(
        self, market, code, start_date, end_date, period, adjusted_price
    ):
        """일봉 조회 호출을 기록하고 단일 구간 가격을 반환한다."""

        self.calls.append((market, code, start_date, end_date, period, adjusted_price))
        prices = [
            self._price("20240401", 10.0),
            self._price("20240402", 11.0),
            self._price("20240403", 12.0),
            self._price("20240404", 13.0),
        ]
        return DailyStockPriceResult(
            summary=DailyStockPriceSummary(name="삼성전자", code="005930"),
            prices=prices,
        )

    def _price(self, date: str, close_price: float):
        """테스트용 DailyStockPrice 객체를 만든다."""

        return DailyStockPrice(
            date=date,
            open_price=close_price,
            high_price=close_price,
            low_price=close_price,
            close_price=close_price,
            accumulated_volume=0,
            accumulated_trading_value=0.0,
            price_diff=0.0,
            price_diff_sign="3",
            change_flag="N",
        )


class CappedApiClient(FakeApiClient):
    """여러 과거 구간 조회가 필요한 상황을 재현하는 API 클라이언트."""

    def get_daily_stock_prices(
        self, market, code, start_date, end_date, period, adjusted_price
    ):
        """조회 종료일에 따라 다른 가격 chunk를 반환한다."""

        self.calls.append((market, code, start_date, end_date, period, adjusted_price))
        if end_date == "20240411":
            prices = [
                self._price("20240409", 9.0),
                self._price("20240410", 10.0),
                self._price("20240411", 11.0),
            ]
        else:
            prices = [
                self._price("20240403", 3.0),
                self._price("20240404", 4.0),
                self._price("20240405", 5.0),
                self._price("20240408", 8.0),
            ]
        return DailyStockPriceResult(
            summary=DailyStockPriceSummary(name="삼성전자", code="005930"),
            prices=prices,
        )


class MovingAverageIndicatorFeatureTest(unittest.TestCase):
    """이동평균 지표 계산과 controller 응답 변환을 검증한다."""

    def test_service_uses_trading_dates_to_fetch_history_for_single_window(self):
        """단일 조회로 충분한 이동평균 선행 이력을 확보하는지 검증한다."""

        api_client = FakeApiClient()
        service = StockQuoteService(api_client)

        result = service.get_moving_average(
            market="J",
            code="005930",
            start_date="20240403",
            end_date="20240404",
            period="D",
            adjusted_price=True,
            window=3,
        )

        self.assertEqual(
            api_client.calls,
            [("J", "005930", "20240329", "20240404", "D", True)],
        )
        self.assertEqual(result.summary.code, "005930")
        self.assertEqual(
            [value.date for value in result.values],
            ["20240403", "20240404"],
        )
        self.assertEqual(result.values[0].moving_average, 11.0)
        self.assertEqual(result.values[1].moving_average, 12.0)

    def test_service_fetches_older_chunks_until_window_history_is_available(self):
        """부족한 이동평균 이력을 과거 chunk 조회로 채우는지 검증한다."""

        api_client = CappedApiClient()
        service = StockQuoteService(api_client)

        result = service.get_moving_average(
            market="J",
            code="005930",
            start_date="20240410",
            end_date="20240411",
            period="D",
            adjusted_price=True,
            window=5,
        )

        self.assertEqual(
            api_client.calls,
            [
                ("J", "005930", "20240401", "20240411", "D", True),
                ("J", "005930", "20240329", "20240408", "D", True),
            ],
        )
        self.assertEqual(
            [value.date for value in result.values],
            ["20240410", "20240411"],
        )
        self.assertAlmostEqual(result.values[0].moving_average, 7.2)
        self.assertAlmostEqual(result.values[1].moving_average, 8.6)

    def test_controller_returns_moving_average_response_schema(self):
        """Controller가 이동평균 결과를 응답 스키마로 변환하는지 검증한다."""

        request = MovingAverageRequest(
            market="J",
            code="005930",
            start_date="20240403",
            end_date="20240404",
            period="D",
            adjusted_price=True,
            window=3,
        )
        service = StockQuoteService(FakeApiClient())

        response = get_moving_average(request, stock_quote_service=service)

        self.assertEqual(response.summary.name, "삼성전자")
        self.assertEqual(response.values[0].date, "20240403")
        self.assertEqual(response.values[0].moving_average, 11.0)

    def test_service_rejects_non_positive_window(self):
        """이동평균 window가 양수가 아니면 예외가 발생하는지 검증한다."""

        service = StockQuoteService(FakeApiClient())

        with self.assertRaises(ValueError):
            service.get_moving_average(
                market="J",
                code="005930",
                start_date="20240403",
                end_date="20240404",
                period="D",
                adjusted_price=True,
                window=0,
            )


if __name__ == "__main__":
    unittest.main()
