import unittest
from unittest.mock import patch

from stock.domain.price import DailyStockPrice
from stock.interface.controller.stock_quote_controller import get_rsi, get_rsi_signal
from stock.interface.schema.stock_quote import RsiRequest, RsiSignalRequest
from stock.service.stock_quote_service import StockQuoteService


class FakeApiClient:
    """RSI 계산에 사용할 짧은 고정 가격 API 클라이언트."""

    def __init__(self):
        """호출 인자를 기록할 목록을 초기화한다."""

        self.calls = []

    def get_daily_stock_prices(
        self, market, code, start_date, end_date, period, adjusted_price
    ):
        """RSI 계산용 일봉 가격을 반환하고 호출 인자를 기록한다."""

        self.calls.append((market, code, start_date, end_date, period, adjusted_price))
        prices = [
            self._price("20240401", 10.0),
            self._price("20240402", 14.0),
            self._price("20240403", 12.0),
            self._price("20240404", 18.0),
        ]
        return [price for price in prices if start_date <= price.date <= end_date]

    def _price(self, date: str, close_price: float):
        """테스트용 DailyStockPrice 객체를 만든다."""

        return DailyStockPrice(
            date=date,
            open_price=0.0,
            high_price=close_price,
            low_price=close_price,
            close_price=close_price,
            accumulated_volume=0,
            accumulated_trading_value=0.0,
            price_diff=0.0,
            price_diff_sign="3",
            change_flag="N",
        )


class HistoricalRsiApiClient(FakeApiClient):
    """요청 구간 앞의 RSI 선행 이력을 포함하는 API 클라이언트."""

    def get_daily_stock_prices(
        self, market, code, start_date, end_date, period, adjusted_price
    ):
        """RSI 범위 필터링 테스트용 일봉 가격을 반환한다."""

        self.calls.append((market, code, start_date, end_date, period, adjusted_price))
        prices = [
            self._price("20240401", 10.0),
            self._price("20240402", 12.0),
            self._price("20240403", 14.0),
            self._price("20240404", 16.0),
            self._price("20240405", 18.0),
            self._price("20240408", 16.0),
            self._price("20240409", 14.0),
            self._price("20240410", 12.0),
        ]
        return [price for price in prices if start_date <= price.date <= end_date]

    def _price(self, date: str, close_price: float):
        """테스트용 DailyStockPrice 객체를 만든다."""

        return DailyStockPrice(
            date=date,
            open_price=0.0,
            high_price=close_price,
            low_price=close_price,
            close_price=close_price,
            accumulated_volume=0,
            accumulated_trading_value=0.0,
            price_diff=0.0,
            price_diff_sign="3",
            change_flag="N",
        )


class RsiIndicatorFeatureTest(unittest.TestCase):
    """RSI 지표 계산과 controller 응답 변환을 검증한다."""

    def test_service_calculates_rsi_from_daily_close_prices(self):
        """서비스가 일봉 종가로 RSI 값을 계산하는지 검증한다."""

        api_client = FakeApiClient()
        service = StockQuoteService(api_client)

        result = service.get_rsi(
            market="J",
            code="005930",
            start_date="20240401",
            end_date="20240404",
            period="D",
            adjusted_price=True,
            rsi_window=3,
        )

        self.assertEqual(
            api_client.calls,
            [("J", "005930", "20240327", "20240404", "D", True)],
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].date, "20240404")
        self.assertAlmostEqual(result[0].value, 83.3333, places=4)

    def test_service_fetches_history_and_returns_requested_rsi_range(self):
        """RSI 계산 이력을 확보한 뒤 요청 구간만 반환하는지 검증한다."""

        api_client = HistoricalRsiApiClient()
        service = StockQuoteService(api_client)

        result = service.get_rsi(
            market="J",
            code="005930",
            start_date="20240405",
            end_date="20240410",
            period="D",
            adjusted_price=True,
            rsi_window=3,
        )

        self.assertEqual(
            api_client.calls,
            [("J", "005930", "20240402", "20240409", "D", True)],
        )
        self.assertEqual(
            [value.date for value in result],
            ["20240405", "20240408", "20240409"],
        )
        self.assertAlmostEqual(result[0].value, 100.0, places=4)
        self.assertAlmostEqual(result[-1].value, 33.3333, places=4)

    def test_controller_returns_rsi_response_schema(self):
        """Controller가 RSI 결과를 응답 스키마로 변환하는지 검증한다."""

        request = RsiRequest(
            market="J",
            code="005930",
            start_date="20240401",
            end_date="20240404",
            period="D",
            adjusted_price=True,
            rsi_window=3,
        )
        service = StockQuoteService(FakeApiClient())

        response = get_rsi(request, stock_quote_service=service)

        self.assertEqual(response[0].date, "20240404")
        self.assertAlmostEqual(response[0].rsi, 83.3333, places=4)

    def test_controller_returns_rsi_signal_response_schema(self):
        """Controller가 RSI 신호 결과를 응답 스키마로 변환하는지 검증한다."""

        request = RsiSignalRequest(
            market="J",
            code="005930",
            start_date="20240405",
            end_date="20240410",
            period="D",
            adjusted_price=True,
            rsi_window=3,
            ema_window=2,
        )
        service = StockQuoteService(HistoricalRsiApiClient())

        with patch("stock.service.stock_quote_service.calculate_ema_warmup_days") as warmup:
            warmup.return_value = 2
            response = get_rsi_signal(request, stock_quote_service=service)

        self.assertEqual(
            [value.signal for value in response],
            ["neutral", "neutral", "neutral"],
        )
        self.assertAlmostEqual(response[-1].rsi_ema, 48.1481, places=4)


if __name__ == "__main__":
    unittest.main()
