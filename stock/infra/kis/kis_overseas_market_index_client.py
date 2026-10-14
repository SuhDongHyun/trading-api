from stock.domain.market import OverseasMarketIndexPrice
from stock.domain.port.overseas_market_index_client import OverseasMarketIndexClient
from stock.infra.kis.kis_http_client import KisHttpClient
from stock.infra.kis.kis_util import (
    DAILY_PERIOD_CODE,
    fetch_daily_chart_prices,
    split_calendar_date_range,
    to_float,
)


class KisOverseasMarketIndexClient(OverseasMarketIndexClient):
    """KIS 해외 지수 API 응답을 일별 시장 지수로 변환한다."""

    def __init__(self, http_client: KisHttpClient):
        self._http_client = http_client

    def get_overseas_market_index_prices(
        self, market: str, code: str, start_date: str, end_date: str
    ) -> list[OverseasMarketIndexPrice]:
        """KIS 일별 해외 시세 요청을 100달력일 단위로 나누어 조회한다."""

        def fetch_page(chunk_start: str, chunk_end: str):
            path = "/uapi/overseas-price/v1/quotations/inquire-daily-chartprice"
            params = {
                "FID_COND_MRKT_DIV_CODE": market,
                "FID_INPUT_ISCD": code,
                "FID_INPUT_DATE_1": chunk_start,
                "FID_INPUT_DATE_2": chunk_end,
                "FID_PERIOD_DIV_CODE": DAILY_PERIOD_CODE,
            }
            resp = self._http_client.get(path, params=params, tr_id="FHKST03030100")
            return resp.json()

        prices = fetch_daily_chart_prices(
            start_date,
            end_date,
            fetch_page,
            split_range=split_calendar_date_range,
        )
        return [
            OverseasMarketIndexPrice(
                date=item["stck_bsop_date"],
                open_price=to_float(item["ovrs_nmix_oprc"]),
                high_price=to_float(item["ovrs_nmix_hgpr"]),
                low_price=to_float(item["ovrs_nmix_lwpr"]),
                close_price=to_float(item["ovrs_nmix_prpr"]),
            )
            for item in prices
        ]
