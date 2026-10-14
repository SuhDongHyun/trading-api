import unittest
from unittest.mock import patch

from stock.infra.kis.kis_client import KISClient


class FakeResponse:
    """KIS 해외 지수 일봉 응답을 흉내낸다."""

    def json(self):
        return {
            "output2": [
                {
                    "stck_bsop_date": "20240531",
                    "ovrs_nmix_oprc": "4100",
                    "ovrs_nmix_hgpr": "4200",
                    "ovrs_nmix_lwpr": "4000",
                    "ovrs_nmix_prpr": "4150",
                }
            ]
        }


class OverseasMarketIndexPriceTest(unittest.TestCase):
    """해외 지수 요청이 일봉으로 고정되는지 검증한다."""

    @patch("stock.infra.kis.kis_client.api_get")
    def test_requests_daily_chart_and_maps_response(self, api_get):
        api_get.return_value = FakeResponse()
        client = KISClient()

        result = client.get_overseas_market_index_prices(
            market="N",
            code="SPX",
            start_date="20240528",
            end_date="20240531",
        )

        api_get.assert_called_once_with(
            path="/uapi/overseas-price/v1/quotations/inquire-daily-chartprice",
            params={
                "FID_COND_MRKT_DIV_CODE": "N",
                "FID_INPUT_ISCD": "SPX",
                "FID_INPUT_DATE_1": "20240528",
                "FID_INPUT_DATE_2": "20240531",
                "FID_PERIOD_DIV_CODE": "D",
            },
            tr_id="FHKST03030100",
        )
        self.assertEqual(result[0].date, "20240531")
        self.assertEqual(result[0].close_price, 4150.0)


if __name__ == "__main__":
    unittest.main()
