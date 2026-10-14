from abc import ABC, abstractmethod

from stock.domain.market import DomesticMarketIndexPrice


class DomesticMarketIndexClient(ABC):
    """KIS 국내 시장 지수 시계열을 제공하는 포트."""

    @abstractmethod
    def get_domestic_market_index_prices(
        self, market: str, code: str, start_date: str, end_date: str
    ) -> list[DomesticMarketIndexPrice]:
        """지정한 기간의 국내 시장 지수 가격을 조회한다."""

        raise NotImplementedError
