import unittest
from unittest.mock import Mock

from stock.infra.kis.kis_overseas_market_index_client import (
    KisOverseasMarketIndexClient,
)


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

    def test_requests_daily_chart_and_maps_response(self):
        http_client = Mock()
        http_client.get.return_value = FakeResponse()
        client = KisOverseasMarketIndexClient(http_client)

        result = client.get_overseas_market_index_prices(
            market="N",
            code="SPX",
            start_date="20240528",
            end_date="20240531",
        )

        http_client.get.assert_called_once_with(
            "/uapi/overseas-price/v1/quotations/inquire-daily-chartprice",
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

    def test_long_range_chunks_by_calendar_days_and_keeps_all_foreign_sessions(self):
        http_client = Mock()

        def row(date: str):
            return {
                "stck_bsop_date": date,
                "ovrs_nmix_oprc": "4100",
                "ovrs_nmix_hgpr": "4200",
                "ovrs_nmix_lwpr": "4000",
                "ovrs_nmix_prpr": "4150",
            }

        http_client.get.side_effect = [
            Mock(
                json=Mock(return_value={"output2": [row("20240409"), row("20240101")]})
            ),
            Mock(
                json=Mock(return_value={"output2": [row("20240501"), row("20240410")]})
            ),
        ]
        client = KisOverseasMarketIndexClient(http_client)

        result = client.get_overseas_market_index_prices(
            market="N",
            code="SPX",
            start_date="20240101",
            end_date="20240501",
        )

        self.assertEqual(
            [price.date for price in result],
            ["20240101", "20240409", "20240410", "20240501"],
        )
        self.assertEqual(http_client.get.call_count, 2)
        self.assertEqual(
            [
                call.kwargs["params"]["FID_INPUT_DATE_1"]
                for call in http_client.get.call_args_list
            ],
            ["20240101", "20240410"],
        )
        self.assertEqual(
            [
                call.kwargs["params"]["FID_INPUT_DATE_2"]
                for call in http_client.get.call_args_list
            ],
            ["20240409", "20240501"],
        )

    def test_chuseok_range_queries_even_without_krx_sessions(self):
        http_client = Mock()
        http_client.get.return_value = Mock(
            json=Mock(
                return_value={
                    "output2": [
                        {
                            "stck_bsop_date": "20240918",
                            "ovrs_nmix_oprc": "4100",
                            "ovrs_nmix_hgpr": "4200",
                            "ovrs_nmix_lwpr": "4000",
                            "ovrs_nmix_prpr": "4150",
                        }
                    ]
                }
            )
        )
        client = KisOverseasMarketIndexClient(http_client)

        result = client.get_overseas_market_index_prices(
            market="N",
            code="SPX",
            start_date="20240914",
            end_date="20240918",
        )

        http_client.get.assert_called_once_with(
            "/uapi/overseas-price/v1/quotations/inquire-daily-chartprice",
            params={
                "FID_COND_MRKT_DIV_CODE": "N",
                "FID_INPUT_ISCD": "SPX",
                "FID_INPUT_DATE_1": "20240914",
                "FID_INPUT_DATE_2": "20240918",
                "FID_PERIOD_DIV_CODE": "D",
            },
            tr_id="FHKST03030100",
        )
        self.assertEqual([price.date for price in result], ["20240918"])


if __name__ == "__main__":
    unittest.main()
