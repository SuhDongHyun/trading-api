from config import KISSetting

from stock.domain.account import Account, AccountSummary, Position
from stock.domain.port.account_client import AccountClient
from stock.infra.kis.kis_http_client import KisHttpClient


class KisAccountClient(AccountClient):
    """KIS 잔고 API 응답을 계좌 도메인 객체로 변환한다."""

    def __init__(self, http_client: KisHttpClient, kis_settings: KISSetting):
        self._http_client = http_client
        self._settings = kis_settings

    def get_account_info(self) -> AccountSummary:
        """KIS 보유 종목과 계좌 요약 응답을 묶어 반환한다."""

        path = "/uapi/domestic-stock/v1/trading/inquire-balance"
        params = {
            "CANO": self._settings.account_num,
            "ACNT_PRDT_CD": self._settings.account_code,
            "AFHR_FLPR_YN": "N",
            "INQR_DVSN": "01",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "Y",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "00",
        }
        resp = self._http_client.get(path=path, params=params, tr_id="TTTC8434R")
        output = resp.json()
        positions = [
            Position(
                code=item["pdno"],
                name=item["prdt_name"],
                quantity=item["hldg_qty"],
                unrealized_pnl=item["evlu_pfls_amt"],
                unrealized_return=item["evlu_pfls_rt"],
            )
            for item in output["output1"]
        ]
        accounts = [
            Account(
                cash_balance=item["dnca_tot_amt"],
                total_pnl=item["asst_icdc_amt"],
                total_return=item["asst_icdc_erng_rt"],
            )
            for item in output["output2"]
        ]
        return AccountSummary(positions=positions, accounts=accounts)
