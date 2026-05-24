import unittest
from unittest.mock import patch

from stock.domain.price import DailyStockPrice
from stock.domain.stock import StockInfo
from stock.interface.controller.stock_quote_controller import get_moving_average
from stock.interface.schema.stock_quote import MovingAverageRequest
from stock.service.indicator.common import (
    calculate_indicator_fetch_start_date,
    normalize_period_end,
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
        """W/M/Y는 period 첫 거래일에서 window-1개 이전 bar까지 조회한다."""

        self.assertEqual(normalize_period_start("20260401", "D"), "20260401")
        self.assertEqual(normalize_period_start("20260401", "W"), "20260330")
        self.assertEqual(normalize_period_start("20260415", "M"), "20260401")
        self.assertEqual(normalize_period_start("20260415", "Y"), "20260102")
        self.assertEqual(normalize_period_start("20260101", "D"), "20260102")
        self.assertEqual(normalize_period_start("20260101", "W"), "20251229")
        self.assertEqual(normalize_period_start("20250315", "M"), "20250304")
        self.assertEqual(normalize_period_start("20260115", "Y"), "20260102")
        self.assertEqual(normalize_period_end("20260415", "M"), "20260430")
        self.assertEqual(normalize_period_end("20260415", "Y"), "20261231")

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
            "20250304",
        )
        self.assertEqual(
            calculate_indicator_fetch_start_date(
                normalize_period_start("20260401", "Y"), "Y", 14
            ),
            "20130102",
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
                    self._price("20260202", 10.0),
                    self._price("20260303", 20.0),
                    self._price("20260401", 30.0),
                    self._price("20260504", 40.0),
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
            [("J", "005930", "20260202", "20260531", "M", True)],
        )
        self.assertEqual(
            [value.date for value in result],
            ["20260401", "20260504"],
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
                    self._price("20240102", 10.0),
                    self._price("20250102", 20.0),
                    self._price("20260102", 30.0),
                    self._price("20270104", 40.0),
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
            [("J", "005930", "20240102", "20271231", "Y", True)],
        )
        self.assertEqual(
            [value.date for value in result],
            ["20260102", "20270104"],
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

    def test_macd_warmup_uses_current_price_as_price_scale(self):
        """MACD EMA warmup은 RSI 범위가 아닌 현재가 스케일로 seed error를 잡는다."""

        class MacdApiClient(FakeApiClient):
            def __init__(self):
                super().__init__()
                self.stock_info_calls = []

            def get_stock_info(self, market, code):
                self.stock_info_calls.append((market, code))
                return StockInfo(
                    market_name="KOSPI",
                    code=code,
                    name="삼성전자",
                    industry="반도체",
                    per=0.0,
                    pbr=0.0,
                    eps=0.0,
                    bps=0.0,
                    open_price=70000.0,
                    current_price=70000.0,
                    previous_price=69000.0,
                    highest_price=71000.0,
                    lowest_price=68000.0,
                    upper_limit_price=90000.0,
                    lower_limit_price=50000.0,
                    current_volume=0,
                    previous_volume=0,
                    current_trading_value=0.0,
                    price_diff=1000.0,
                    price_diff_rate=1.4,
                )

        api_client = MacdApiClient()
        service = StockQuoteService(api_client)

        with patch("stock.service.stock_quote_service.calculate_ema_warmup_days") as warmup:
            warmup.return_value = 3

            service.get_macd(
                market="J",
                code="005930",
                start_date="20240403",
                end_date="20240404",
                period="D",
                adjusted_price=True,
                ema_short_window=12,
                ema_long_window=26,
            )

        self.assertEqual(api_client.stock_info_calls, [("J", "005930")])
        warmup.assert_called_once_with(26, "D", max_seed_error=14000.0)

    def test_macd_warmup_accepts_current_price_string_from_adapter(self):
        """KIS adapter가 문자열 현재가를 넘겨도 MACD warmup 스케일을 계산한다."""

        class StringPriceMacdApiClient(FakeApiClient):
            def get_stock_info(self, market, code):
                return StockInfo(
                    market_name="KOSPI",
                    code=code,
                    name="삼성전자",
                    industry="반도체",
                    per=0.0,
                    pbr=0.0,
                    eps=0.0,
                    bps=0.0,
                    open_price=70000.0,
                    current_price="70000",
                    previous_price=69000.0,
                    highest_price=71000.0,
                    lowest_price=68000.0,
                    upper_limit_price=90000.0,
                    lower_limit_price=50000.0,
                    current_volume=0,
                    previous_volume=0,
                    current_trading_value=0.0,
                    price_diff=1000.0,
                    price_diff_rate=1.4,
                )

        service = StockQuoteService(StringPriceMacdApiClient())

        with patch("stock.service.stock_quote_service.calculate_ema_warmup_days") as warmup:
            warmup.return_value = 3

            service.get_macd(
                market="J",
                code="005930",
                start_date="20240403",
                end_date="20240404",
                period="D",
                adjusted_price=True,
                ema_short_window=12,
                ema_long_window=26,
            )

        warmup.assert_called_once_with(26, "D", max_seed_error=14000.0)


if __name__ == "__main__":
    unittest.main()
