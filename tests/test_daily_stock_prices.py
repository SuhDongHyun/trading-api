import unittest
from unittest.mock import Mock

from stock.domain.stock import DailyStockPrice
from stock.infra.kis.kis_stock_quote_client import KisStockQuoteClient
from stock.interface.controller.stock_quote_controller import get_daily_stock_prices
from stock.interface.schema.stock_quote import StockInfoResponse
from stock.interface.schema.stock_quote import HistoricalStockQuoteRequest
from stock.service.stock_quote_service import StockQuoteService


class FakeResponse:
    """KIS 일봉 API의 최소 JSON 응답을 흉내낸다."""

    def json(self):
        """KIS 일봉 응답 body를 반환한다."""

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


class FakeQuoteClient:
    """일봉 서비스 테스트에 사용할 고정 응답 API 클라이언트."""

    def __init__(self):
        """호출 인자를 기록할 목록을 초기화한다."""

        self.calls = []

    def get_daily_stock_prices(
        self, market, code, start_date, end_date, adjusted_price
    ):
        """일봉 조회 호출 인자를 기록하고 고정 결과를 반환한다."""

        self.calls.append((market, code, start_date, end_date, adjusted_price))
        return [
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
        ]


class DailyStockPriceFeatureTest(unittest.TestCase):
    """일봉 조회 서비스, KIS adapter, controller 동작을 검증한다."""

    def test_kis_client_maps_stock_info_code_and_normalizes_numbers(self):
        """현재가 응답은 요청 종목 코드를 보존하고 숫자 필드를 정규화한다."""

        info = {
            "rprs_mrkt_kor_name": "KOSPI",
            "bstp_cls_code": "0001",
            "prdt_abrv_name": "삼성전자",
            "bstp_kor_isnm": "전기전자",
            "per": "12.5",
            "pbr": "",
            "eps": "",
            "bps": "9000",
            "stck_oprc": "70000",
            "stck_prpr": "70100",
            "stck_prdy_clpr": "69000",
            "stck_hgpr": "71000",
            "stck_lwpr": "68000",
            "stck_mxpr": "89700",
            "stck_llam": "48300",
            "acml_vol": "123",
            "prdy_vol": "",
            "acml_tr_pbmn": "123456",
            "prdy_vrss": "1100",
            "prdy_ctrt": "1.59",
        }
        responses = [Mock() for _ in range(3)]
        for response in responses:
            response.json.return_value = {"output": info}
        http_client = Mock()
        http_client.get.side_effect = responses
        client = KisStockQuoteClient(http_client)

        result = client.get_stock_info("J", "005930")

        self.assertEqual(result.code, "005930")
        self.assertEqual(result.industry, "전기전자")
        self.assertEqual(result.per, 12.5)
        self.assertIsNone(result.pbr)
        self.assertIsNone(result.eps)
        self.assertEqual(StockInfoResponse.model_validate(result).per, 12.5)
        self.assertIsNone(StockInfoResponse.model_validate(result).pbr)
        self.assertEqual(result.current_price, 70100.0)
        self.assertEqual(result.current_volume, 123)
        self.assertEqual(result.previous_volume, 0)
        self.assertEqual(result.current_trading_value, 123456.0)

    def test_service_delegates_daily_price_query_to_quote_client(self):
        """서비스가 일봉 조회 요청을 API 클라이언트로 위임하는지 검증한다."""

        quote_client = FakeQuoteClient()
        service = StockQuoteService(quote_client)

        result = service.get_daily_stock_prices(
            market="J",
            code="005930",
            start_date="20240401",
            end_date="20240430",
            adjusted_price=True,
        )

        self.assertEqual(
            quote_client.calls,
            [("J", "005930", "20240401", "20240430", True)],
        )
        self.assertEqual(result[0].date, "20240401")

    def test_service_keeps_price_history_logic_inside_stock_quote_service(self):
        """가격 이력 조회 책임을 별도 서비스로 노출하지 않는지 검증한다."""

        service = StockQuoteService(FakeQuoteClient())

        self.assertFalse(hasattr(service, "price_history_service"))

    def test_kis_client_calls_daily_chart_endpoint_and_maps_response(self):
        """KIS client가 일봉 endpoint 호출 결과를 도메인 객체로 매핑하는지 검증한다."""

        http_client = Mock()
        http_client.get.return_value = FakeResponse()
        client = KisStockQuoteClient(http_client)

        result = client.get_daily_stock_prices(
            market="J",
            code="005930",
            start_date="20240401",
            end_date="20240430",
            adjusted_price=True,
        )

        http_client.get.assert_called_once_with(
            "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
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
        self.assertEqual(result[0].date, "20240401")
        self.assertEqual(result[0].close_price, 70500.0)
        self.assertEqual(result[0].accumulated_volume, 1234567)

    def test_controller_returns_daily_price_response_schema(self):
        """Controller가 일봉 도메인 결과를 응답 스키마로 변환하는지 검증한다."""

        request = HistoricalStockQuoteRequest(
            market="J",
            code="005930",
            start_date="20240401",
            end_date="20240430",
            adjusted_price=True,
        )
        service = StockQuoteService(FakeQuoteClient())

        response = get_daily_stock_prices(request, stock_quote_service=service)

        self.assertEqual(response[0].date, "20240401")
        self.assertEqual(response[0].close_price, 70500.0)


if __name__ == "__main__":
    unittest.main()
