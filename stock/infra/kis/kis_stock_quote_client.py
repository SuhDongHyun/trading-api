from stock.domain.port.stock_quote_client import StockQuoteClient
from stock.domain.stock import DailyStockPrice, StockInfo
from stock.infra.kis.kis_http_client import KisHttpClient
from stock.infra.kis.kis_util import (
    DAILY_PERIOD_CODE,
    fetch_daily_chart_prices,
    to_float,
    to_int,
    to_optional_float,
)


class KisStockQuoteClient(StockQuoteClient):
    """KIS 종목 현재가와 일봉 API 응답을 시세 도메인 객체로 변환한다."""

    def __init__(self, http_client: KisHttpClient):
        self._http_client = http_client

    def get_stock_info(self, market: str, code: str) -> StockInfo:
        """기본 정보와 현재가를 결합하고 요청한 종목 식별자를 보존한다."""

        def get_output(path: str, params: dict[str, str], tr_id: str):
            return self._http_client.get(path, params=params, tr_id=tr_id).json()[
                "output"
            ]

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
            code=code,
            name=stock_info["prdt_abrv_name"],
            industry=stock_info["bstp_kor_isnm"],
            per=to_optional_float(stock_info["per"]),
            pbr=to_optional_float(stock_info["pbr"]),
            eps=to_optional_float(stock_info["eps"]),
            bps=to_optional_float(stock_info["bps"]),
            open_price=to_float(stock_info["stck_oprc"]),
            current_price=to_float(stock_info["stck_prpr"]),
            previous_price=to_float(stock_info["stck_prdy_clpr"]),
            highest_price=to_float(stock_info["stck_hgpr"]),
            lowest_price=to_float(stock_info["stck_lwpr"]),
            upper_limit_price=to_float(stock_info["stck_mxpr"]),
            lower_limit_price=to_float(stock_info["stck_llam"]),
            current_volume=to_int(stock_info["acml_vol"]),
            previous_volume=to_int(stock_info["prdy_vol"]),
            current_trading_value=to_float(stock_info["acml_tr_pbmn"]),
            price_diff=to_float(stock_info["prdy_vrss"]),
            price_diff_rate=to_float(stock_info["prdy_ctrt"]),
        )

    def get_daily_stock_prices(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        adjusted_price: bool = True,
    ) -> list[DailyStockPrice]:
        """각 KIS 요청이 최대 100건을 반환하므로 구간별 조회 결과를 합친다."""

        def fetch_page(chunk_start: str, chunk_end: str):
            path = "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
            params = {
                "FID_COND_MRKT_DIV_CODE": market,
                "FID_INPUT_ISCD": code,
                "FID_INPUT_DATE_1": chunk_start,
                "FID_INPUT_DATE_2": chunk_end,
                "FID_PERIOD_DIV_CODE": DAILY_PERIOD_CODE,
                "FID_ORG_ADJ_PRC": "0" if adjusted_price else "1",
            }
            resp = self._http_client.get(path, params=params, tr_id="FHKST03010100")
            return resp.json()

        prices = fetch_daily_chart_prices(start_date, end_date, fetch_page)
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
