import unittest

from stock.domain.stock import (
    DailyStockPrice,
    DailyStockPriceResult,
    DailyStockPriceSummary,
)
from stock.interface.controller.stock_quote_controller import get_rsi, get_rsi_signal
from stock.interface.schema.stock_quote import RsiRequest, RsiSignalRequest
from stock.service.stock_quote_service import StockQuoteService


class FakeApiClient:
    def __init__(self):
        self.calls = []

    def get_daily_stock_prices(
        self, market, code, start_date, end_date, period, adjusted_price
    ):
        self.calls.append((market, code, start_date, end_date, period, adjusted_price))
        prices = [
            self._price("20240401", 10.0),
            self._price("20240402", 14.0),
            self._price("20240403", 12.0),
            self._price("20240404", 18.0),
        ]
        return DailyStockPriceResult(
            summary=DailyStockPriceSummary(name="삼성전자", code="005930"),
            prices=prices,
        )

    def _price(self, date: str, close_price: float):
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
    def get_daily_stock_prices(
        self, market, code, start_date, end_date, period, adjusted_price
    ):
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
        return DailyStockPriceResult(
            summary=DailyStockPriceSummary(name="삼성전자", code="005930"),
            prices=prices,
        )

    def _price(self, date: str, close_price: float):
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
    def test_service_calculates_rsi_from_daily_close_prices(self):
        api_client = FakeApiClient()
        service = StockQuoteService(api_client)

        result = service.get_rsi(
            market="J",
            code="005930",
            start_date="20240401",
            end_date="20240404",
            period="D",
            adjusted_price=True,
            rsi_period=3,
        )

        self.assertEqual(
            api_client.calls,
            [("J", "005930", "20240326", "20240404", "D", True)],
        )
        self.assertEqual(result.summary.code, "005930")
        self.assertEqual(len(result.values), 1)
        self.assertEqual(result.values[0].date, "20240404")
        self.assertAlmostEqual(result.values[0].rsi, 83.3333, places=4)

    def test_service_fetches_history_and_returns_requested_rsi_range(self):
        api_client = HistoricalRsiApiClient()
        service = StockQuoteService(api_client)

        result = service.get_rsi(
            market="J",
            code="005930",
            start_date="20240405",
            end_date="20240410",
            period="D",
            adjusted_price=True,
            rsi_period=3,
        )

        self.assertEqual(
            api_client.calls,
            [("J", "005930", "20240330", "20240410", "D", True)],
        )
        self.assertEqual(
            [value.date for value in result.values],
            ["20240405", "20240408", "20240409", "20240410"],
        )
        self.assertAlmostEqual(result.values[0].rsi, 100.0, places=4)
        self.assertAlmostEqual(result.values[-1].rsi, 29.6296, places=4)

    def test_controller_returns_rsi_response_schema(self):
        request = RsiRequest(
            market="J",
            code="005930",
            start_date="20240401",
            end_date="20240404",
            period="D",
            adjusted_price=True,
            rsi_period=3,
        )
        service = StockQuoteService(FakeApiClient())

        response = get_rsi(request, stock_quote_service=service)

        self.assertEqual(response.summary.name, "삼성전자")
        self.assertEqual(response.values[0].date, "20240404")
        self.assertAlmostEqual(response.values[0].rsi, 83.3333, places=4)

    def test_controller_returns_rsi_signal_response_schema(self):
        request = RsiSignalRequest(
            market="J",
            code="005930",
            start_date="20240405",
            end_date="20240410",
            period="D",
            adjusted_price=True,
            rsi_period=3,
            overbought_threshold=70.0,
            oversold_threshold=30.0,
        )
        service = StockQuoteService(HistoricalRsiApiClient())

        response = get_rsi_signal(request, stock_quote_service=service)

        self.assertEqual(response.summary.name, "삼성전자")
        self.assertEqual(
            [value.signal for value in response.values],
            ["OVERBOUGHT", "NEUTRAL", "NEUTRAL", "OVERSOLD"],
        )
        self.assertAlmostEqual(response.values[-1].rsi, 29.6296, places=4)


if __name__ == "__main__":
    unittest.main()
