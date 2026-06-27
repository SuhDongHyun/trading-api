import requests

from config import settings
from common.exchange_calendar import get_krx_calendar
from stock.domain.market import VKospiIndex
from stock.domain.adapter.domestic_index_client import IDomesticIndexClient


VKOSPI_INDEX_NAME = "코스피 200 변동성지수"


class KRXClient(IDomesticIndexClient):
    """KRX Open API 응답을 국내 지수 데이터로 변환하는 어댑터."""

    def _get_derivative_index(self, date: str, type: str) -> dict:
        """기준일의 KRX 파생상품지수 일별시세를 DataFrame으로 조회한다."""

        res = requests.get(
            "https://data-dbg.krx.co.kr/svc/apis/idx/drvprod_dd_trd",
            params={"basDd": date},
            headers={"AUTH_KEY": settings.krx.api_key},
            timeout=10,
        )
        res.raise_for_status()
        items = res.json().get("OutBlock_1", [])
        return next(
            (item for item in items if item.get("IDX_NM") == type),
            None,
        )

    def get_vkospi_index(self, start_date: str, end_date: str) -> list[VKospiIndex]:
        """KRX 파생상품지수 일별시세를 조회한다."""

        vkospi_items = [
            self._get_derivative_index(
                session.strftime("%Y%m%d"), "코스피 200 변동성지수"
            )
            for session in get_krx_calendar().sessions_in_range(start_date, end_date)
        ]

        return [
            VKospiIndex(
                date=item["BAS_DD"],
                open_price=float(item["OPNPRC_IDX"]),
                high_price=float(item["HGPRC_IDX"]),
                low_price=float(item["LWPRC_IDX"]),
                close_price=float(item["CLSPRC_IDX"]),
                price_diff=float(item["CMPPREVDD_IDX"]),
                price_diff_rate=float(item["FLUC_RT"]),
            )
            for item in vkospi_items
            if item is not None
        ]
