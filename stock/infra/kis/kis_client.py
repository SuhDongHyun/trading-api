from config import settings

from stock.domain.account import Position, Account, AccountSummary
from stock.domain.adapter.api_client import IApiClient
from stock.infra.kis.kis_http_client import api_get


class KISClient(IApiClient):
    def get_account_info(self) -> AccountSummary:
        path = "/uapi/domestic-stock/v1/trading/inquire-balance"
        params = {
            "CANO": settings.kis.account_num,
            "ACNT_PRDT_CD": settings.kis.account_code,
            "AFHR_FLPR_YN": "N",
            "INQR_DVSN": "01",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "Y",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "00",
        }
        resp = api_get(path=path, params=params, tr_id="TTTC8434R")
        positions = [
            Position(
                code=output["pdno"],
                name=output["prdt_name"],
                quantity=output["hldg_qty"],
                unrealized_pnl=output["evlu_pfls_amt"],
                unrealized_return=output["evlu_pfls_rt"],
            )
            for output in resp.json()["output1"]
        ]
        accounts = [
            Account(
                cash_balance=output["dnca_tot_amt"],
                total_pnl=output["asst_icdc_amt"],
                total_return=output["asst_icdc_erng_rt"],
            )
            for output in resp.json()["output2"]
        ]

        return AccountSummary(
            positions=positions,
            accounts=accounts,
        )
