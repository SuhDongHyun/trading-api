import logging
from itertools import chain
from datetime import datetime

from config import settings

from stock.domain.account import Position, Account, AccountSummary
from stock.domain.stock import StockInfo
from stock.domain.price import DailyStockPrice
from stock.domain.news import News
from stock.domain.market import (
    DomesticMarketIndicatorPrice,
    OverseasMarketIndicatorPrice,
)
from stock.domain.adapter.api_client import IApiClient
from stock.infra.kis.kis_http_client import api_get
from stock.infra.kis.kis_util import to_float, to_int, split_date_range

logger = logging.getLogger(__name__)


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

        date_ranges = split_date_range(start_date, end_date, period)
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

    def _get_news(
        self,
        code: str,
        search_date: str,
        search_time: str,
    ) -> list[dict]:
        """KIS 뉴스 검색 응답을 뉴스 목록으로 변환한다."""

        path = "/uapi/domestic-stock/v1/quotations/news-title"
        params = {
            "FID_NEWS_OFER_ENTP_CODE": "",
            "FID_COND_MRKT_CLS_CODE": "",
            "FID_INPUT_ISCD": code,
            "FID_TITL_CNTT": "",
            "FID_INPUT_DATE_1": search_date,
            "FID_INPUT_HOUR_1": search_time,
            "FID_RANK_SORT_CLS_CODE": "",
            "FID_INPUT_SRNO": "",
        }

        logger.info(
            "Requesting KIS news code=%s search_date=%s search_time=%s params=%s",
            code,
            search_date,
            search_time,
            params,
        )
        resp = api_get(path=path, params=params, tr_id="FHKST01011800")
        news_list = resp.json()["output"]
        return news_list

    def get_total_news(
        self,
        code: str,
        search_date: str,
        search_time: str,
    ) -> list[News]:
        """KIS 뉴스 검색 API의 페이지 제한에 맞춰 검색 시각을 갱신하며, 지정 날짜의 지정 시간까지 발행된 종목 관련 뉴스를 모두 조회한다."""
        news_by_key: dict[str, News] = {}
        search_day = datetime.strptime(search_date, "%Y%m%d").date()

        while True:
            news_list = self._get_news(code, search_date, search_time)
            code_cols = ["iscd1", "iscd2", "iscd3", "iscd4", "iscd5"]
            target_news = [
                News(
                    key=news["cntt_usiq_srno"],
                    title=news["hts_pbnt_titl_cntt"],
                    source=news["dorg"],
                    published_at=datetime.strptime(
                        news["data_dt"] + news["data_tm"], "%Y%m%d%H%M%S"
                    ),
                )
                for news in news_list
                if any(news.get(col) == code for col in code_cols)
            ]

            before_count = len(news_by_key)

            for news in target_news:
                if news.key not in news_by_key:
                    news_by_key[news.key] = news

            if len(news_list) < 40 or len(news_by_key) == before_count:
                break

            last_published_at = target_news[-1].published_at
            if last_published_at.date() < search_day:
                break

            search_time = last_published_at.strftime("%H%M%S")

        return [
            news
            for news in list(news_by_key.values())
            if news.published_at.strftime("%Y%m%d") == search_date
        ]

    def get_domestic_market_indicator_prices(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        period: str,
    ) -> list[DomesticMarketIndicatorPrice]:
        """지정한 기간의 국내 KIS 지표 가격을 조회한다."""

        start_day = datetime.strptime(start_date, "%Y%m%d")
        end_day = datetime.strptime(end_date, "%Y%m%d")
        path = "/uapi/domestic-stock/v1/quotations/inquire-daily-indexchartprice"
        params = {
            "FID_COND_MRKT_DIV_CODE": market,
            "FID_INPUT_ISCD": code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date,
            "FID_PERIOD_DIV_CODE": period,
        }
        resp = api_get(path=path, params=params, tr_id="FHKUP03500100")
        prices_by_date = {
            price_day: price
            for price in resp.json()["output2"]
            if start_day
            <= (price_day := datetime.strptime(price["stck_bsop_date"], "%Y%m%d"))
            <= end_day
        }

        return [
            DomesticMarketIndicatorPrice(
                date=price["stck_bsop_date"],
                open_price=to_float(price["bstp_nmix_oprc"]),
                high_price=to_float(price["bstp_nmix_hgpr"]),
                low_price=to_float(price["bstp_nmix_lwpr"]),
                close_price=to_float(price["bstp_nmix_prpr"]),
                price_diff=to_float(price["bstp_nmix_prdy_vrss"]),
                price_diff_rate=to_float(price["bstp_nmix_prdy_ctrt"]),
                volume=to_int(price["acml_vol"]),
                trading_value=to_float(price["acml_tr_pbmn"]),
            )
            for _, price in sorted(prices_by_date.items())
        ]

    def get_overseas_market_indicator_prices(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        period: str,
    ):
        """해외 KIS 지표 차트 응답을 요약과 가격 목록으로 변환한다."""

        date_ranges = split_date_range(start_date, end_date, period)
        bodies = []

        for _start_date, _end_date in date_ranges:
            path = "/uapi/overseas-price/v1/quotations/inquire-daily-chartprice"
            params = {
                "FID_COND_MRKT_DIV_CODE": market,
                "FID_INPUT_ISCD": code,
                "FID_INPUT_DATE_1": _start_date,
                "FID_INPUT_DATE_2": _end_date,
                "FID_PERIOD_DIV_CODE": period,
            }
            resp = api_get(path=path, params=params, tr_id="FHKST03030100")
            bodies.append(resp.json())

        prices = list(chain.from_iterable(body["output2"][::-1] for body in bodies))

        return [
            OverseasMarketIndicatorPrice(
                date=price["stck_bsop_date"],
                open_price=to_float(price["ovrs_nmix_oprc"]),
                high_price=to_float(price["ovrs_nmix_hgpr"]),
                low_price=to_float(price["ovrs_nmix_lwpr"]),
                close_price=to_float(price["ovrs_nmix_prpr"]),
            )
            for price in prices
        ]
