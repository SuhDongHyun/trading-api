from abc import ABC, abstractmethod


class IMarketClient(ABC):
    """시장 관련 정보를 제공하는 포트."""

    @abstractmethod
    def get_fear_and_greed_index(self):
        """현재 시장의 공포탐욕지수를 조회한다."""

        raise NotImplementedError

    @abstractmethod
    def get_vix_index(self, start_date: str, end_date: str):
        """현재 시장의 VIX 지수를 조회한다."""

        raise NotImplementedError
