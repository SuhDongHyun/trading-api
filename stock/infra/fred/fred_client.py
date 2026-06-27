import fear_and_greed
from fredapi import Fred

from config import settings
from stock.domain.market import FearAndGreedIndex, VIXIndex
from stock.domain.adapter.overseas_index_client import IOverseasIndexClient


FEAR_AND_GREED_CONDITION_RANGES = (
    (24, "EXTREME FEAR"),
    (44, "FEAR"),
    (55, "NEUTRAL"),
    (75, "GREED"),
    (100, "EXTREME GREED"),
)


class FredClient(IOverseasIndexClient):
    """FRED API 응답을 시장 지표 도메인 값으로 변환하는 어댑터."""

    def __init__(self):
        self.fred = Fred(api_key=settings.fred.api_key)

    def get_fear_and_greed_index(self) -> FearAndGreedIndex:
        fear_and_greed_index = fear_and_greed.get()
        condition = next(
            condition
            for max_value, condition in FEAR_AND_GREED_CONDITION_RANGES
            if fear_and_greed_index.value <= max_value
        )
        return FearAndGreedIndex(
            value=fear_and_greed_index.value,
            condition=condition,
            updated_at=fear_and_greed_index.last_update,
        )

    def get_vix_index(self, start_date: str, end_date: str):
        vix_index = self.fred.get_series(
            "VIXCLS", observation_start=start_date, observation_end=end_date
        )
        valid_vix_index = vix_index[vix_index.notna()].copy()
        return [
            VIXIndex(date=index.strftime("%Y%m%d"), value=value)
            for index, value in valid_vix_index.items()
        ]
