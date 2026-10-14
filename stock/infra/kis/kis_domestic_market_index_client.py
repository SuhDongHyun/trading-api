from datetime import datetime, timedelta

from stock.domain.market import DomesticMarketIndexPrice
from stock.domain.port.domestic_market_index_client import DomesticMarketIndexClient
from stock.infra.kis.kis_http_client import KisHttpClient
from stock.infra.kis.kis_util import DAILY_PERIOD_CODE, to_float, to_int


class KisDomesticMarketIndexClient(DomesticMarketIndexClient):
    """KIS 국내 지수 API 응답을 일별 시장 지수로 변환한다."""

    def __init__(self, http_client: KisHttpClient):
        self._http_client = http_client

    def get_domestic_market_index_prices(
        self, market: str, code: str, start_date: str, end_date: str
    ) -> list[DomesticMarketIndexPrice]:
        """KIS의 역방향 페이지 조회를 날짜 구간이 덮일 때까지 이어간다."""

        start_day = datetime.strptime(start_date, "%Y%m%d")
        end_day = datetime.strptime(end_date, "%Y%m%d")
        prices_by_date = {}
        cursor_date = end_date

        while True:
            path = "/uapi/domestic-stock/v1/quotations/inquire-index-daily-price"
            params = {
                "FID_COND_MRKT_DIV_CODE": market,
                "FID_INPUT_ISCD": code,
                "FID_INPUT_DATE_1": cursor_date,
                "FID_PERIOD_DIV_CODE": DAILY_PERIOD_CODE,
            }
            resp = self._http_client.get(path, params=params, tr_id="FHPUP02120000")
            prices = resp.json()["output2"]
            if not prices:
                break

            dated_prices = [
                (datetime.strptime(item["stck_bsop_date"], "%Y%m%d"), item)
                for item in prices
            ]
            for price_day, item in dated_prices:
                if start_day <= price_day <= end_day:
                    prices_by_date[price_day] = item

            earliest_day = min(price_day for price_day, _ in dated_prices)
            if earliest_day <= start_day:
                break
            cursor_date = (earliest_day - timedelta(days=1)).strftime("%Y%m%d")

        return [
            DomesticMarketIndexPrice(
                date=item["stck_bsop_date"],
                open_price=to_float(item["bstp_nmix_oprc"]),
                high_price=to_float(item["bstp_nmix_hgpr"]),
                low_price=to_float(item["bstp_nmix_lwpr"]),
                close_price=to_float(item["bstp_nmix_prpr"]),
                price_diff=to_float(item["bstp_nmix_prdy_vrss"]),
                price_diff_rate=to_float(item["bstp_nmix_prdy_ctrt"]),
                volume=to_int(item["acml_vol"]),
                trading_value=to_float(item["acml_tr_pbmn"]),
            )
            for _, item in sorted(prices_by_date.items())
        ]
