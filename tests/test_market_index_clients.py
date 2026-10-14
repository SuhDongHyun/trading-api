from datetime import datetime
from unittest.mock import Mock

from common.min_interval_throttle import MinIntervalThrottle
from stock.domain.port.domestic_market_index_client import DomesticMarketIndexClient
from stock.domain.port.fear_greed_client import FearGreedClient
from stock.domain.port.korea_stock_list_client import KoreaStockListClient
from stock.domain.port.overseas_market_index_client import OverseasMarketIndexClient
from stock.domain.port.vix_client import VixClient
from stock.domain.port.vkospi_client import VkospiClient
from stock.domain.port.account_client import AccountClient
from stock.domain.port.news_client import NewsClient
from stock.domain.port.stock_quote_client import StockQuoteClient
from stock.infra.fred.fred_client import FredClient
from stock.infra.cnn.fear_greed_client import CnnFearGreedClient
from stock.infra.kis.kis_account_client import KisAccountClient
from stock.infra.kis.kis_domestic_market_index_client import (
    KisDomesticMarketIndexClient,
)
from stock.infra.kis.kis_news_client import KisNewsClient
from stock.infra.kis.kis_overseas_market_index_client import (
    KisOverseasMarketIndexClient,
)
from stock.infra.kis.kis_stock_quote_client import KisStockQuoteClient
from stock.infra.krx.krx_client import KRX_API_MIN_INTERVAL_SECONDS, KRXClient
from stock.infra.krx import krx_client


def test_adapters_implement_role_specific_ports():
    """각 외부 어댑터가 제공하는 역할별 포트만 구현한다."""

    assert issubclass(KisAccountClient, AccountClient)
    assert issubclass(KisStockQuoteClient, StockQuoteClient)
    assert issubclass(KisNewsClient, NewsClient)
    assert issubclass(KisDomesticMarketIndexClient, DomesticMarketIndexClient)
    assert issubclass(KisOverseasMarketIndexClient, OverseasMarketIndexClient)
    assert issubclass(FredClient, VixClient)
    assert issubclass(CnnFearGreedClient, FearGreedClient)
    assert issubclass(KRXClient, KoreaStockListClient)
    assert issubclass(KRXClient, VkospiClient)


def test_krx_client_requests_derivative_index_daily_prices(monkeypatch):
    """KRX 파생상품지수 일별시세 API 응답에서 대상 지수를 선택한다."""

    response = Mock()
    response.json.return_value = {
        "OutBlock_1": [
            {"BAS_DD": "20260625", "IDX_NM": "다른 지수", "CLSPRC_IDX": "99.99"},
            {
                "BAS_DD": "20260625",
                "IDX_NM": "코스피 200 변동성지수",
                "CLSPRC_IDX": "19.43",
            },
        ]
    }
    requests_get = Mock(return_value=response)
    monkeypatch.setattr(krx_client.requests, "get", requests_get)

    client = KRXClient(api_key="test-key")
    result = client._get_derivative_index("20260625", "코스피 200 변동성지수")

    requests_get.assert_called_once_with(
        "https://data-dbg.krx.co.kr/svc/apis/idx/drvprod_dd_trd",
        params={"basDd": "20260625"},
        headers={"AUTH_KEY": "test-key"},
        timeout=10,
    )
    response.raise_for_status.assert_called_once_with()
    assert result == {
        "BAS_DD": "20260625",
        "IDX_NM": "코스피 200 변동성지수",
        "CLSPRC_IDX": "19.43",
    }


def test_krx_client_throttles_sequential_vkospi_requests(monkeypatch):
    """거래일별 VKOSPI 조회 사이에 짧은 간격을 유지한다."""

    calendar = Mock()
    calendar.sessions_in_range.return_value = [
        datetime(2026, 6, 25),
        datetime(2026, 6, 26),
    ]
    monkeypatch.setattr(krx_client, "get_krx_calendar", lambda: calendar)

    def make_response(date: str, close: str):
        response = Mock()
        response.json.return_value = {
            "OutBlock_1": [
                {
                    "BAS_DD": date,
                    "IDX_NM": "코스피 200 변동성지수",
                    "OPNPRC_IDX": "19.0",
                    "HGPRC_IDX": "20.0",
                    "LWPRC_IDX": "18.0",
                    "CLSPRC_IDX": close,
                    "CMPPREVDD_IDX": "0.5",
                    "FLUC_RT": "2.5",
                }
            ]
        }
        return response

    requests_get = Mock(
        side_effect=[make_response("20260625", "19.5"), make_response("20260626", "20.0")]
    )
    monkeypatch.setattr(krx_client.requests, "get", requests_get)
    throttle = Mock(spec=MinIntervalThrottle)
    client = KRXClient(api_key="test-key", min_interval_throttle=throttle)

    result = client.get_vkospi_index("20260625", "20260626")

    assert [item.date for item in result] == ["20260625", "20260626"]
    assert [item.close_price for item in result] == [19.5, 20.0]
    assert [call.kwargs["params"] for call in requests_get.call_args_list] == [
        {"basDd": "20260625"},
        {"basDd": "20260626"},
    ]
    assert KRX_API_MIN_INTERVAL_SECONDS == 0.1
    assert throttle.acquire.call_count == 2
