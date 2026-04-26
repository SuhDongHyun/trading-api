import unittest

from stock.domain.stock import (
    DailyStockPrice,
    DailyStockPriceResult,
    DailyStockPriceSummary,
)
from stock.interface.controller.stock_quote_controller import get_overbought_oversold
from stock.interface.schema.stock_quote import OverboughtOversoldRequest
from stock.service.stock_quote_service import StockQuoteService


class FakeApiClient:
    def __init__(self):
        self.calls = []

    def get_daily_stock_prices(
        self, market, code, start_date, end_date, period, adjusted_price
    ):
        self.calls.append((market, code, start_date, end_date, period, adjusted_price))
        return DailyStockPriceResult(
            summary=DailyStockPriceSummary(name="삼성전자", code="005930"),
            prices=[
                self._price("20240401", 10.0),
                self._price("20240402", 14.0),
                self._price("20240403", 12.0),
                self._price("20240404", 18.0),
            ],
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


class OverboughtOversoldSignalFeatureTest(unittest.TestCase):
    def test_service_returns_overbought_signal_from_rsi_and_stochastic(self):
        api_client = FakeApiClient()
        service = StockQuoteService(api_client)

        result = service.get_overbought_oversold(
            market="J",
            code="005930",
            start_date="20240401",
            end_date="20240404",
            period="D",
            adjusted_price=True,
            rsi_period=3,
            stochastic_k_period=3,
            stochastic_k_smoothing_period=1,
            stochastic_d_period=1,
        )

        self.assertEqual(
            api_client.calls,
            [("J", "005930", "20240401", "20240404", "D", True)],
        )
        self.assertEqual(result.summary.code, "005930")
        self.assertEqual(len(result.values), 1)
        self.assertEqual(result.values[0].date, "20240404")
        self.assertEqual(result.values[0].signal, "OVERBOUGHT")
        self.assertAlmostEqual(result.values[0].rsi, 83.3333, places=4)
        self.assertAlmostEqual(result.values[0].slow_k, 100.0, places=4)
        self.assertAlmostEqual(result.values[0].slow_d, 100.0, places=4)

    def test_controller_returns_overbought_oversold_response_schema(self):
        request = OverboughtOversoldRequest(
            market="J",
            code="005930",
            start_date="20240401",
            end_date="20240404",
            period="D",
            adjusted_price=True,
            rsi_period=3,
            stochastic_k_period=3,
            stochastic_k_smoothing_period=1,
            stochastic_d_period=1,
        )
        service = StockQuoteService(FakeApiClient())

        response = get_overbought_oversold(request, stock_quote_service=service)

        self.assertEqual(response.summary.name, "삼성전자")
        self.assertEqual(response.values[0].date, "20240404")
        self.assertEqual(response.values[0].signal, "OVERBOUGHT")
        self.assertAlmostEqual(response.values[0].rsi, 83.3333, places=4)


if __name__ == "__main__":
    unittest.main()
