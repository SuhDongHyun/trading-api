from abc import ABC, abstractmethod

from stock.domain.market import FearAndGreedIndex


class FearGreedClient(ABC):
    """CNN 공포탐욕지수를 제공하는 포트."""

    @abstractmethod
    def get_fear_and_greed_index(self) -> FearAndGreedIndex:
        """현재 공포탐욕지수와 상태를 조회한다."""

        raise NotImplementedError
