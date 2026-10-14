from fredapi import Fred

from stock.domain.market import VIXIndex
from stock.domain.port.vix_client import VixClient


class FredClient(VixClient):
    """FRED VIX 시계열을 시장 지표 도메인 값으로 변환한다."""

    def __init__(self, api_key: str):
        self.fred = Fred(api_key=api_key)

    def get_vix_index(self, start_date: str, end_date: str):
        """FRED VIXCLS 관측치에서 값이 없는 날을 제외해 반환한다."""

        vix_index = self.fred.get_series(
            "VIXCLS", observation_start=start_date, observation_end=end_date
        )
        valid_vix_index = vix_index[vix_index.notna()].copy()
        return [
            VIXIndex(date=index.strftime("%Y%m%d"), value=value)
            for index, value in valid_vix_index.items()
        ]
