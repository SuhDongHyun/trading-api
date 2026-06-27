from abc import ABC, abstractmethod


class IDomesticIndexClient(ABC):
    """국내 시장 지수 정보를 제공하는 포트."""

    @abstractmethod
    def get_vkospi_index(self, start_date: str, end_date: str):
        """국내 시장의 VKOSPI 지수를 조회한다."""

        raise NotImplementedError
