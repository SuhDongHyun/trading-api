import fear_and_greed

from stock.domain.market import FearAndGreedIndex
from stock.domain.port.fear_greed_client import FearGreedClient

FEAR_AND_GREED_CONDITION_RANGES = (
    (24, "EXTREME FEAR"),
    (44, "FEAR"),
    (55, "NEUTRAL"),
    (75, "GREED"),
    (100, "EXTREME GREED"),
)


class CnnFearGreedClient(FearGreedClient):
    """CNN 공포탐욕 응답에 범위별 시장 상태를 붙여 반환한다."""

    def get_fear_and_greed_index(self) -> FearAndGreedIndex:
        """CNN 지수 값에 맞는 상태 구간을 선택한다."""

        index = fear_and_greed.get()
        condition = next(
            label
            for max_value, label in FEAR_AND_GREED_CONDITION_RANGES
            if index.value <= max_value
        )
        return FearAndGreedIndex(
            value=index.value,
            condition=condition,
            updated_at=index.last_update,
        )
