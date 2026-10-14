import unittest
from unittest.mock import patch

from common.exchange_calendar import get_krx_calendar
from stock.domain.stock import DailyStockPrice
from stock.interface.controller.stock_quote_controller import get_moving_average
from stock.interface.schema.stock_quote import MovingAverageRequest
from stock.service.indicator.moving_average import calculate_macd_values
from stock.service.stock_quote_service import StockQuoteService


class FakeQuoteClient:
    """이동평균 계산에 사용할 고정 일봉 가격 API 클라이언트."""

    def __init__(self):
        """호출 인자를 기록할 목록을 초기화한다."""

        self.calls = []

    def get_daily_stock_prices(
        self, market, code, start_date, end_date, adjusted_price
    ):
        """일봉 조회 호출을 기록하고 단일 구간 가격을 반환한다."""

        self.calls.append((market, code, start_date, end_date, adjusted_price))
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


class CappedQuoteClient(FakeQuoteClient):
    """여러 과거 구간 조회가 필요한 상황을 재현하는 API 클라이언트."""

    def get_daily_stock_prices(
        self, market, code, start_date, end_date, adjusted_price
    ):
        """조회 종료일에 따라 다른 가격 chunk를 반환한다."""

        self.calls.append((market, code, start_date, end_date, adjusted_price))
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

        quote_client = FakeQuoteClient()
        service = StockQuoteService(quote_client)

        result = service.get_moving_average(
            market="J",
            code="005930",
            start_date="20240403",
            end_date="20240404",
            adjusted_price=True,
            window=3,
        )

        self.assertEqual(
            quote_client.calls,
            [("J", "005930", "20240401", "20240404", True)],
        )
        self.assertEqual(
            [value.date for value in result],
            ["20240403", "20240404"],
        )
        self.assertEqual(result[0].value, 11.0)
        self.assertEqual(result[1].value, 12.0)

    def test_service_fetches_exact_daily_window_history(self):
        """일봉 이동평균 계산에 필요한 거래일 이력만 조회하는지 검증한다."""

        quote_client = CappedQuoteClient()
        service = StockQuoteService(quote_client)

        result = service.get_moving_average(
            market="J",
            code="005930",
            start_date="20240410",
            end_date="20240411",
            adjusted_price=True,
            window=5,
        )

        self.assertEqual(
            quote_client.calls,
            [("J", "005930", "20240404", "20240411", True)],
        )
        self.assertEqual(
            [value.date for value in result],
            ["20240409", "20240410", "20240411"],
        )
        self.assertEqual([value.value for value in result], [5.8, 7.2, 8.6])

    def test_controller_returns_moving_average_response_schema(self):
        """Controller가 이동평균 결과를 응답 스키마로 변환하는지 검증한다."""

        request = MovingAverageRequest(
            market="J",
            code="005930",
            start_date="20240403",
            end_date="20240404",
            adjusted_price=True,
            window=3,
        )
        service = StockQuoteService(FakeQuoteClient())

        response = get_moving_average(request, stock_quote_service=service)

        self.assertEqual(response[0].date, "20240403")
        self.assertEqual(response[0].moving_average, 11.0)

    def test_service_returns_empty_result_when_available_history_is_short(self):
        """부분 이력은 정의할 수 있는 이동평균이 없어 빈 결과를 반환한다."""

        service = StockQuoteService(FakeQuoteClient())

        result = service.get_moving_average(
            market="J",
            code="005930",
            start_date="20240403",
            end_date="20240404",
            window=5,
        )

        self.assertEqual(result, [])

    def test_macd_warmup_uses_daily_close_without_stock_info_request(self):
        """MACD warm-up은 요청 구간 종가를 사용해 현재가 API 호출을 생략한다."""

        class MacdQuoteClient(FakeQuoteClient):
            def __init__(self):
                super().__init__()
                self.daily_calls = []
                self.prices = [
                    self._price("20240401", 68000.0),
                    self._price("20240402", 69000.0),
                    self._price("20240403", 70000.0),
                    self._price("20240404", 71000.0),
                ]

            def get_daily_stock_prices(
                self, market, code, start_date, end_date, adjusted_price
            ):
                self.daily_calls.append(
                    (market, code, start_date, end_date, adjusted_price)
                )
                return [
                    price
                    for price in self.prices
                    if start_date <= price.date <= end_date
                ]

        quote_client = MacdQuoteClient()
        service = StockQuoteService(quote_client)

        with patch(
            "stock.service.stock_quote_service.calculate_ema_warmup_days"
        ) as warmup:
            warmup.return_value = 3

            result = service.get_macd(
                market="J",
                code="005930",
                start_date="20240403",
                end_date="20240404",
                adjusted_price=True,
                ema_short_window=12,
                ema_long_window=26,
            )

        self.assertEqual(
            quote_client.daily_calls,
            [
                ("J", "005930", "20240403", "20240404", True),
                ("J", "005930", "20240401", "20240402", True),
            ],
        )
        self.assertEqual([value.date for value in result], ["20240403", "20240404"])
        warmup.assert_called_once_with(26, max_seed_error=14200.0)

    def test_macd_allows_an_empty_warmup_for_a_newly_listed_stock(self):
        """상장 전 선행 구간이 비어도 요청 구간의 MACD 결과를 반환한다."""

        class NewlyListedQuoteClient(FakeQuoteClient):
            def __init__(self):
                super().__init__()
                self.daily_calls = []
                self.daily_results = []
                self.prices = [
                    self._price(session.strftime("%Y%m%d"), 100.0 + index)
                    for index, session in enumerate(
                        get_krx_calendar().sessions_in_range("20250102", "20250131")
                    )
                ]

            def get_daily_stock_prices(
                self, market, code, start_date, end_date, adjusted_price
            ):
                self.daily_calls.append(
                    (market, code, start_date, end_date, adjusted_price)
                )
                result = [
                    price
                    for price in self.prices
                    if start_date <= price.date <= end_date
                ]
                self.daily_results.append(result)
                return result

        quote_client = NewlyListedQuoteClient()
        service = StockQuoteService(quote_client)

        with patch(
            "stock.service.stock_quote_service.calculate_ema_warmup_days",
            return_value=3,
        ):
            result = service.get_macd(
                market="J",
                code="NEW001",
                start_date="20241201",
                end_date="20250131",
                ema_short_window=12,
                ema_long_window=26,
            )

        self.assertEqual(len(quote_client.daily_calls), 2)
        self.assertEqual(quote_client.daily_results[1], [])
        self.assertEqual(
            result,
            calculate_macd_values(quote_client.prices, 12, 26, ema_warmup_days=3),
        )


if __name__ == "__main__":
    unittest.main()
