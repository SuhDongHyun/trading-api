from abc import ABC, abstractmethod

from stock.domain.market import OverseasMarketIndexPrice


class OverseasMarketIndexClient(ABC):
    """KIS 해외 시장 지수 시계열을 제공하는 포트."""

    @abstractmethod
    def get_overseas_market_index_prices(
        self, market: str, code: str, start_date: str, end_date: str
    ) -> list[OverseasMarketIndexPrice]:
        """지정한 기간의 해외 시장 지수 가격을 조회한다."""

        raise NotImplementedError
