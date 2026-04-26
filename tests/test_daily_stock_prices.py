import unittest
from unittest.mock import patch

from stock.domain.stock import (
    DailyStockPrice,
    DailyStockPriceResult,
    DailyStockPriceSummary,
)
from stock.infra.kis.kis_client import KISClient
from stock.interface.controller.stock_quote_controller import get_daily_stock_prices
from stock.interface.schema.stock_quote import DailyStockPriceRequest
from stock.service.stock_quote_service import StockQuoteService


class FakeResponse:
    def json(self):
        return {
            "output1": {
                "hts_kor_isnm": "삼성전자",
                "stck_shrn_iscd": "005930",
            },
            "output2": [
                {
                    "stck_bsop_date": "20240401",
                    "stck_oprc": "70000",
                    "stck_hgpr": "71000",
                    "stck_lwpr": "69000",
                    "stck_clpr": "70500",
                    "acml_vol": "1234567",
                    "acml_tr_pbmn": "87654321000",
                    "flng_cls_code": "00",
                    "prtt_rate": "0.00",
                    "mod_yn": "N",
                    "prdy_vrss_sign": "2",
                    "prdy_vrss": "500",
                    "revl_issu_reas": "",
                }
            ],
        }


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
                DailyStockPrice(
                    date="20240401",
                    open_price=70000.0,
                    high_price=71000.0,
                    low_price=69000.0,
                    close_price=70500.0,
                    accumulated_volume=1234567,
                    accumulated_trading_value=87654321000.0,
                    price_diff=500.0,
                    price_diff_sign="2",
                    change_flag="N",
                )
            ],
        )


class DailyStockPriceFeatureTest(unittest.TestCase):
    def test_service_delegates_daily_price_query_to_api_client(self):
        api_client = FakeApiClient()
        service = StockQuoteService(api_client)

        result = service.get_daily_stock_prices(
            market="J",
            code="005930",
            start_date="20240401",
            end_date="20240430",
            period="D",
            adjusted_price=True,
        )

        self.assertEqual(
            api_client.calls,
            [("J", "005930", "20240401", "20240430", "D", True)],
        )
        self.assertEqual(result.summary.code, "005930")

    @patch("stock.infra.kis.kis_client.api_get")
    def test_kis_client_calls_daily_chart_endpoint_and_maps_response(self, api_get):
        api_get.return_value = FakeResponse()
        client = KISClient()

        result = client.get_daily_stock_prices(
            market="J",
            code="005930",
            start_date="20240401",
            end_date="20240430",
            period="D",
            adjusted_price=True,
        )

        api_get.assert_called_once_with(
            path="/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
            params={
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": "005930",
                "FID_INPUT_DATE_1": "20240401",
                "FID_INPUT_DATE_2": "20240430",
                "FID_PERIOD_DIV_CODE": "D",
                "FID_ORG_ADJ_PRC": "0",
            },
            tr_id="FHKST03010100",
        )
        self.assertEqual(result.summary.name, "삼성전자")
        self.assertEqual(result.summary.code, "005930")
        self.assertEqual(result.prices[0].date, "20240401")
        self.assertEqual(result.prices[0].close_price, 70500.0)
        self.assertEqual(result.prices[0].accumulated_volume, 1234567)

    def test_controller_returns_daily_price_response_schema(self):
        request = DailyStockPriceRequest(
            market="J",
            code="005930",
            start_date="20240401",
            end_date="20240430",
            period="D",
            adjusted_price=True,
        )
        service = StockQuoteService(FakeApiClient())

        response = get_daily_stock_prices(request, stock_quote_service=service)

        self.assertEqual(response.summary.code, "005930")
        self.assertEqual(response.prices[0].date, "20240401")
        self.assertEqual(response.prices[0].close_price, 70500.0)


if __name__ == "__main__":
    unittest.main()
