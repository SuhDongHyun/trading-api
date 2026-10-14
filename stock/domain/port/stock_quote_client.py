from abc import ABC, abstractmethod

from stock.domain.stock import DailyStockPrice, StockInfo


class StockQuoteClient(ABC):
    """국내 종목의 현재가와 일봉 시세를 제공하는 포트."""

    @abstractmethod
    def get_stock_info(self, market: str, code: str) -> StockInfo:
        """단일 종목의 현재 시세 정보를 조회한다."""

        raise NotImplementedError

    @abstractmethod
    def get_daily_stock_prices(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        adjusted_price: bool,
    ) -> list[DailyStockPrice]:
        """지정 기간의 일봉 가격 목록을 조회한다."""

        raise NotImplementedError
