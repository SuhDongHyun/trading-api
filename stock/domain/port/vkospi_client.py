from abc import ABC, abstractmethod

from stock.domain.market import VKospiIndex


class VkospiClient(ABC):
    """VKOSPI 시계열을 제공하는 포트."""

    @abstractmethod
    def get_vkospi_index(self, start_date: str, end_date: str) -> list[VKospiIndex]:
        """지정 구간의 VKOSPI 시계열을 조회한다."""

        raise NotImplementedError
