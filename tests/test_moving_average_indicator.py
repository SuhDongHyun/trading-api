import unittest

from stock.domain.stock import (
    DailyStockPrice,
    DailyStockPriceResult,
    DailyStockPriceSummary,
)
from stock.interface.controller.stock_quote_controller import get_moving_average
from stock.interface.schema.stock_quote import MovingAverageRequest
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
            self._price("20240402", 11.0),
            self._price("20240403", 12.0),
            self._price("20240404", 13.0),
        ]
        return DailyStockPriceResult(
            summary=DailyStockPriceSummary(name="삼성전자", code="005930"),
            prices=prices,
        )

    def _price(self, date: str, close_price: float):
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
    def get_daily_stock_prices(
        self, market, code, start_date, end_date, period, adjusted_price
    ):
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
    def test_service_uses_trading_dates_to_fetch_history_for_single_window(self):
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
