from unittest.mock import Mock

from config import KISSetting
from stock.infra.kis.kis_account_client import KisAccountClient


def test_account_client_normalizes_kis_numeric_fields():
    """보유 수량은 int, 계좌 금액·손익·수익률은 float로 정규화한다."""

    response = Mock()
    response.json.return_value = {
        "output1": [
            {
                "pdno": "005930",
                "prdt_name": "삼성전자",
                "hldg_qty": "2",
                "evlu_pfls_amt": "1500",
                "evlu_pfls_rt": "1.25",
            }
        ],
        "output2": [
            {
                "dnca_tot_amt": "50000",
                "asst_icdc_amt": "1500",
                "asst_icdc_erng_rt": "1.25",
            }
        ],
    }
    http_client = Mock()
    http_client.get.return_value = response
    client = KisAccountClient(
        http_client=http_client,
        kis_settings=KISSetting(
            base_url="https://example.test",
            account_num="12345678",
            account_code="01",
            appkey="test-key",
            appsecret="test-secret",
        ),
    )

    result = client.get_account_info()

    assert result.positions[0].quantity == 2
    assert result.positions[0].unrealized_pnl == 1500.0
    assert result.positions[0].unrealized_return == 1.25
    assert result.accounts[0].cash_balance == 50000.0
    assert result.accounts[0].total_pnl == 1500.0
    assert result.accounts[0].total_return == 1.25
    assert isinstance(result.positions[0].quantity, int)
    assert all(
        isinstance(value, float)
        for value in (
            result.positions[0].unrealized_pnl,
            result.positions[0].unrealized_return,
            result.accounts[0].cash_balance,
            result.accounts[0].total_pnl,
            result.accounts[0].total_return,
        )
    )
