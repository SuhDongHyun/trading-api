import unittest
from unittest.mock import call, patch

from stock.infra.kis.kis_client import KISClient


class FakeResponse:
    """KIS 국내 시장 지수 API 응답을 흉내낸다."""

    def __init__(self, prices):
        self.prices = prices

    def json(self):
        return {"output2": self.prices}


def make_price(date: str, close_price: str) -> dict:
    """테스트용 국내 시장 지수 가격을 생성한다."""

    return {
        "stck_bsop_date": date,
        "bstp_nmix_oprc": close_price,
        "bstp_nmix_hgpr": close_price,
        "bstp_nmix_lwpr": close_price,
        "bstp_nmix_prpr": close_price,
        "bstp_nmix_prdy_vrss": "1.0",
        "bstp_nmix_prdy_ctrt": "0.1",
        "acml_vol": "100",
        "acml_tr_pbmn": "1000",
    }


class DomesticMarketIndexPriceTest(unittest.TestCase):
    """국내 시장 지수의 기간 조회 동작을 검증한다."""

    @patch("stock.infra.kis.kis_client.api_get")
    def test_rejects_invalid_date_before_requesting_api(self, api_get):
        client = KISClient()

        with self.assertRaises(ValueError):
            client.get_domestic_market_index_prices(
                market="U",
                code="0001",
                start_date="20241301",
                end_date="20240531",
                period="D",
            )

        api_get.assert_not_called()

    @patch("stock.infra.kis.kis_client.api_get")
    def test_requests_date_range_and_returns_prices_in_date_order(self, api_get):
        api_get.return_value = FakeResponse(
            [
                make_price("20240531", "2700"),
                make_price("20240530", "2690"),
                make_price("20240529", "2680"),
                make_price("20240528", "2670"),
            ]
        )
        client = KISClient()

        result = client.get_domestic_market_index_prices(
            market="U",
            code="0001",
            start_date="20240528",
            end_date="20240531",
            period="D",
        )

        api_get.assert_called_once_with(
            path=(
                "/uapi/domestic-stock/v1/quotations/"
                "inquire-index-daily-price"
            ),
            params={
                "FID_COND_MRKT_DIV_CODE": "U",
                "FID_INPUT_ISCD": "0001",
                "FID_INPUT_DATE_1": "20240531",
                "FID_PERIOD_DIV_CODE": "D",
            },
            tr_id="FHPUP02120000",
        )
        self.assertEqual(
            [price.date for price in result],
            ["20240528", "20240529", "20240530", "20240531"],
        )

    @patch("stock.infra.kis.kis_client.api_get")
    def test_walks_backward_with_cursor_date_until_start_date_is_covered(
        self, api_get
    ):
        api_get.side_effect = [
            FakeResponse(
                [
                    make_price("20240626", "2800"),
                    make_price("20240625", "2790"),
                    make_price("20240501", "2700"),
                ]
            ),
            FakeResponse(
                [
                    make_price("20240430", "2690"),
                    make_price("20240429", "2680"),
                    make_price("20240426", "2670"),
                ]
            ),
        ]
        client = KISClient()

        result = client.get_domestic_market_index_prices(
            market="U",
            code="0001",
            start_date="20240429",
            end_date="20240626",
            period="D",
        )

        self.assertEqual(
            api_get.call_args_list,
            [
                call(
                    path=(
                        "/uapi/domestic-stock/v1/quotations/"
                        "inquire-index-daily-price"
                    ),
                    params={
                        "FID_COND_MRKT_DIV_CODE": "U",
                        "FID_INPUT_ISCD": "0001",
                        "FID_INPUT_DATE_1": "20240626",
                        "FID_PERIOD_DIV_CODE": "D",
                    },
                    tr_id="FHPUP02120000",
                ),
                call(
                    path=(
                        "/uapi/domestic-stock/v1/quotations/"
                        "inquire-index-daily-price"
                    ),
                    params={
                        "FID_COND_MRKT_DIV_CODE": "U",
                        "FID_INPUT_ISCD": "0001",
                        "FID_INPUT_DATE_1": "20240430",
                        "FID_PERIOD_DIV_CODE": "D",
                    },
                    tr_id="FHPUP02120000",
                ),
            ],
        )
        self.assertEqual(
            [price.date for price in result],
            ["20240429", "20240430", "20240501", "20240625", "20240626"],
        )


if __name__ == "__main__":
    unittest.main()
