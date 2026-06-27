from unittest.mock import Mock, patch

from stock.domain.adapter.domestic_index_client import IDomesticIndexClient
from stock.domain.adapter.composite_index_client import ICompositeIndexClient
from stock.domain.adapter.overseas_index_client import IOverseasIndexClient
from stock.infra.fred.fred_client import FredClient
from stock.infra.krx.krx_client import KRXClient
from stock.infra.market.market_index_client import MarketIndexClient


def test_market_index_client_contracts_match_adapter_roles():
    """시장 지수 adapter는 역할별 포트만 구현한다."""

    assert issubclass(FredClient, IOverseasIndexClient)
    assert issubclass(KRXClient, IDomesticIndexClient)
    assert issubclass(MarketIndexClient, ICompositeIndexClient)


@patch("stock.infra.krx.krx_client.settings.krx.api_key", "test-key")
@patch("stock.infra.krx.krx_client.requests.get")
def test_krx_client_requests_derivative_index_daily_prices(requests_get):
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
    requests_get.return_value = response

    client = KRXClient()
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
