from abc import ABC, abstractmethod

from stock.domain.market import VIXIndex


class VixClient(ABC):
    """VIX 시계열을 제공하는 포트."""

    @abstractmethod
    def get_vix_index(self, start_date: str, end_date: str) -> list[VIXIndex]:
        """지정한 기간의 VIX 시계열을 조회한다."""

        raise NotImplementedError
