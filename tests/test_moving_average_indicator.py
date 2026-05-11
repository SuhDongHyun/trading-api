import unittest

from stock.domain.price import DailyStockPrice
from stock.interface.controller.stock_quote_controller import get_moving_average
from stock.interface.schema.stock_quote import MovingAverageRequest
from stock.service.indicator.common import (
    calculate_indicator_fetch_start_date,
    normalize_period_start,
)
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
        return prices

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
        prices = [
            self._price("20240403", 3.0),
            self._price("20240404", 4.0),
            self._price("20240405", 5.0),
            self._price("20240408", 8.0),
            self._price("20240409", 9.0),
            self._price("20240410", 10.0),
            self._price("20240411", 11.0),
        ]
        return prices


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
            [("J", "005930", "20240401", "20240404", "D", True)],
        )
        self.assertEqual(
            [value.date for value in result],
            ["20240403", "20240404"],
        )
        self.assertEqual(result[0].value, 11.0)
        self.assertEqual(result[1].value, 12.0)

    def test_service_fetches_exact_daily_window_history(self):
        """일봉 이동평균 계산에 필요한 거래일 이력만 조회하는지 검증한다."""

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
            [("J", "005930", "20240404", "20240411", "D", True)],
        )
        self.assertEqual(
            [value.date for value in result],
            ["20240409", "20240410", "20240411"],
        )
        self.assertEqual([value.value for value in result], [5.8, 7.2, 8.6])

    def test_calculates_fetch_start_from_period_anchor(self):
        """W/M/Y는 period 기준 시작일에서 window-1개 이전 bar까지 조회한다."""

        self.assertEqual(normalize_period_start("20260401", "D"), "20260401")
        self.assertEqual(normalize_period_start("20260401", "W"), "20260330")
        self.assertEqual(normalize_period_start("20260415", "M"), "20260401")
        self.assertEqual(normalize_period_start("20260415", "Y"), "20260101")

        self.assertEqual(
            calculate_indicator_fetch_start_date("20260401", "D", 14),
            "20260313",
        )
        self.assertEqual(
            calculate_indicator_fetch_start_date(
                normalize_period_start("20260401", "W"), "W", 14
            ),
            "20251229",
        )
        self.assertEqual(
            calculate_indicator_fetch_start_date("20260401", "M", 14),
            "20250301",
        )
        self.assertEqual(
            calculate_indicator_fetch_start_date(
                normalize_period_start("20260401", "Y"), "Y", 14
            ),
            "20130101",
        )

    def test_weekly_moving_average_filters_by_week_anchor(self):
        """주봉은 요청일이 속한 주의 월요일부터 응답에 포함한다."""

        class WeeklyApiClient(FakeApiClient):
            def get_daily_stock_prices(
                self, market, code, start_date, end_date, period, adjusted_price
            ):
                self.calls.append(
                    (market, code, start_date, end_date, period, adjusted_price)
                )
                return [
                    self._price("20260316", 10.0),
                    self._price("20260323", 20.0),
                    self._price("20260330", 30.0),
                    self._price("20260406", 40.0),
                ]

        api_client = WeeklyApiClient()
        service = StockQuoteService(api_client)

        result = service.get_moving_average(
            market="J",
            code="005930",
            start_date="20260401",
            end_date="20260410",
            period="W",
            adjusted_price=True,
            window=3,
        )

        self.assertEqual(
            api_client.calls,
            [("J", "005930", "20260316", "20260406", "W", True)],
        )
        self.assertEqual(
            [value.date for value in result],
            ["20260330", "20260406"],
        )
        self.assertEqual(result[0].value, 20.0)
        self.assertEqual(result[1].value, 30.0)

    def test_monthly_moving_average_filters_by_month_anchor(self):
        """월봉은 요청일이 속한 월의 1일부터 응답에 포함한다."""

        class MonthlyApiClient(FakeApiClient):
            def get_daily_stock_prices(
                self, market, code, start_date, end_date, period, adjusted_price
            ):
                self.calls.append(
                    (market, code, start_date, end_date, period, adjusted_price)
                )
                return [
                    self._price("20260201", 10.0),
                    self._price("20260301", 20.0),
                    self._price("20260401", 30.0),
                    self._price("20260501", 40.0),
                ]

        api_client = MonthlyApiClient()
        service = StockQuoteService(api_client)

        result = service.get_moving_average(
            market="J",
            code="005930",
            start_date="20260415",
            end_date="20260520",
            period="M",
            adjusted_price=True,
            window=3,
        )

        self.assertEqual(
            api_client.calls,
            [("J", "005930", "20260201", "20260501", "M", True)],
        )
        self.assertEqual(
            [value.date for value in result],
            ["20260401", "20260501"],
        )
        self.assertEqual(result[0].value, 20.0)
        self.assertEqual(result[1].value, 30.0)

    def test_yearly_moving_average_filters_by_year_anchor(self):
        """년봉은 요청일이 속한 연도의 1월 1일부터 응답에 포함한다."""

        class YearlyApiClient(FakeApiClient):
            def get_daily_stock_prices(
                self, market, code, start_date, end_date, period, adjusted_price
            ):
                self.calls.append(
                    (market, code, start_date, end_date, period, adjusted_price)
                )
                return [
                    self._price("20240101", 10.0),
                    self._price("20250101", 20.0),
                    self._price("20260101", 30.0),
                    self._price("20270101", 40.0),
                ]

        api_client = YearlyApiClient()
        service = StockQuoteService(api_client)

        result = service.get_moving_average(
            market="J",
            code="005930",
            start_date="20260415",
            end_date="20270520",
            period="Y",
            adjusted_price=True,
            window=3,
        )

        self.assertEqual(
            api_client.calls,
            [("J", "005930", "20240101", "20270101", "Y", True)],
        )
        self.assertEqual(
            [value.date for value in result],
            ["20260101", "20270101"],
        )
        self.assertEqual(result[0].value, 20.0)
        self.assertEqual(result[1].value, 30.0)

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

        self.assertEqual(response[0].date, "20240403")
        self.assertEqual(response[0].moving_average, 11.0)

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
