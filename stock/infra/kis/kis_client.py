from itertools import chain

from config import settings

from stock.domain.account import Position, Account, AccountSummary
from stock.domain.adapter.api_client import IApiClient
from stock.domain.price import DailyStockPrice
from stock.domain.stock import StockInfo
from stock.infra.kis.kis_http_client import api_get
from stock.infra.kis.kis_util import to_float, to_int, split_date_range


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

    def get_stock_info(self, market: str, code: str) -> StockInfo:
        """KIS 현재가 조회 응답을 Stock 도메인 객체로 변환한다."""

        def get_output(path, params, tr_id):
            return api_get(path=path, params=params, tr_id=tr_id).json()["output"]

        stock_info = (
            get_output(
                "/uapi/domestic-stock/v1/quotations/search-stock-info",
                {"PRDT_TYPE_CD": "300", "PDNO": code},
                "CTPF1002R",
            )
            | get_output(
                "/uapi/domestic-stock/v1/quotations/inquire-price",
                {"FID_COND_MRKT_DIV_CODE": market, "FID_INPUT_ISCD": code},
                "FHKST01010100",
            )
            | get_output(
                "/uapi/domestic-stock/v1/quotations/inquire-price-2",
                {"FID_COND_MRKT_DIV_CODE": market, "FID_INPUT_ISCD": code},
                "FHPST01010000",
            )
        )

        return StockInfo(
            market_name=stock_info["rprs_mrkt_kor_name"],
            code=stock_info["bstp_cls_code"],
            name=stock_info["prdt_abrv_name"],
            industry=stock_info["bstp_kor_isnm"],
            per=stock_info["per"],
            pbr=stock_info["pbr"],
            eps=stock_info["eps"],
            bps=stock_info["bps"],
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
    ) -> list[DailyStockPrice]:
        """KIS 일봉 차트 응답을 요약과 가격 목록으로 변환한다."""

        date_ranges = split_date_range(start_date, end_date)
        bodies = []

        for _start_date, _end_date in date_ranges:
            path = "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
            params = {
                "FID_COND_MRKT_DIV_CODE": market,
                "FID_INPUT_ISCD": code,
                "FID_INPUT_DATE_1": _start_date,
                "FID_INPUT_DATE_2": _end_date,
                "FID_PERIOD_DIV_CODE": period,
                "FID_ORG_ADJ_PRC": "0" if adjusted_price else "1",
            }
            resp = api_get(path=path, params=params, tr_id="FHKST03010100")
            bodies.append(resp.json())

        prices = list(chain.from_iterable(body["output2"][::-1] for body in bodies))

        return [
            DailyStockPrice(
                date=price["stck_bsop_date"],
                open_price=to_float(price["stck_oprc"]),
                high_price=to_float(price["stck_hgpr"]),
                low_price=to_float(price["stck_lwpr"]),
                close_price=to_float(price["stck_clpr"]),
                accumulated_volume=to_int(price["acml_vol"]),
                accumulated_trading_value=to_float(price["acml_tr_pbmn"]),
                price_diff=to_float(price["prdy_vrss"]),
                price_diff_sign=price["prdy_vrss_sign"],
                change_flag=price["mod_yn"],
            )
            for price in prices
        ]
