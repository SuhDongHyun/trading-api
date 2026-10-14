from abc import ABC, abstractmethod

from stock.domain.stock import StockMetaInfo


class KoreaStockListClient(ABC):
    """국내 상장 종목 목록을 제공하는 포트."""

    @abstractmethod
    def get_korea_stock_list(self) -> list[StockMetaInfo]:
        """국내 상장 종목 목록을 조회한다."""

        raise NotImplementedError
