from config import settings

from stock.domain.account import Position, Account, AccountSummary
from stock.domain.stock import (
    DailyStockPrice,
    DailyStockPriceResult,
    DailyStockPriceSummary,
    Stock,
)
from stock.domain.adapter.api_client import IApiClient
from stock.infra.kis.kis_http_client import api_get


def _to_float(value: str | int | float | None) -> float:
    """KIS 응답의 빈 문자열 숫자 필드를 float 기본값으로 정규화한다."""

    if value in (None, ""):
        return 0.0
    return float(value)


def _to_int(value: str | int | float | None) -> int:
    """KIS 응답의 빈 문자열 숫자 필드를 int 기본값으로 정규화한다."""

    if value in (None, ""):
        return 0
    return int(float(value))


class KISClient(IApiClient):
    """한국투자증권 Open API 응답을 내부 도메인 객체로 변환하는 어댑터."""

    def get_account_info(self) -> AccountSummary:
        """KIS 잔고 조회 응답을 AccountSummary로 변환한다."""

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

    def get_stock_info(self, market: str, code: str) -> Stock:
        """KIS 현재가 조회 응답을 Stock 도메인 객체로 변환한다."""

        path = "/uapi/domestic-stock/v1/quotations/inquire-price-2"
        params = {
            "FID_COND_MRKT_DIV_CODE": market,
            "FID_INPUT_ISCD": code,
        }
        resp = api_get(path=path, params=params, tr_id="FHPST01010000")
        stock_info = resp.json()["output"]

        return Stock(
            market_name=stock_info["rprs_mrkt_kor_name"],
            code=stock_info["bstp_cls_code"],
            industry=stock_info["bstp_kor_isnm"],
            open_price=stock_info["stck_oprc"],
            current_price=stock_info["stck_prpr"],
            previous_price=stock_info["stck_prdy_clpr"],
            highest_price=stock_info["stck_hgpr"],
            lowest_price=stock_info["stck_lwpr"],
            upper_limit_price=stock_info["stck_mxpr"],
            lower_limit_price=stock_info["stck_llam"],
            current_volume=stock_info["acml_vol"],
            previous_volume=stock_info["prdy_vol"],
            current_trading_value=stock_info["acml_tr_pbmn"],
            price_diff=stock_info["prdy_vrss"],
            price_diff_rate=stock_info["prdy_ctrt"],
        )

    def get_daily_stock_prices(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        period: str,
        adjusted_price: bool = True,
    ) -> DailyStockPriceResult:
        """KIS 일봉 차트 응답을 요약과 가격 목록으로 변환한다."""

        path = "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
        params = {
            "FID_COND_MRKT_DIV_CODE": market,
            "FID_INPUT_ISCD": code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date,
            "FID_PERIOD_DIV_CODE": period,
            "FID_ORG_ADJ_PRC": "0" if adjusted_price else "1",
        }
        resp = api_get(path=path, params=params, tr_id="FHKST03010100")
        body = resp.json()
        summary = body["output1"]

        return DailyStockPriceResult(
            summary=DailyStockPriceSummary(
                name=summary["hts_kor_isnm"],
                code=summary["stck_shrn_iscd"],
            ),
            prices=[
                DailyStockPrice(
                    date=price["stck_bsop_date"],
                    open_price=_to_float(price["stck_oprc"]),
                    high_price=_to_float(price["stck_hgpr"]),
                    low_price=_to_float(price["stck_lwpr"]),
                    close_price=_to_float(price["stck_clpr"]),
                    accumulated_volume=_to_int(price["acml_vol"]),
                    accumulated_trading_value=_to_float(price["acml_tr_pbmn"]),
                    price_diff=_to_float(price["prdy_vrss"]),
                    price_diff_sign=price["prdy_vrss_sign"],
                    change_flag=price["mod_yn"],
                )
                for price in body["output2"]
            ],
        )
