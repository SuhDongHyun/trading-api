from abc import ABC, abstractmethod


class IApiClient(ABC):
    """서비스 계층이 외부 증권사 API 구현에 의존하지 않도록 하는 포트."""

    @abstractmethod
    def get_account_info(self):
        raise NotImplementedError

    @abstractmethod
    def get_stock_info(self, market: str, code: str):
        raise NotImplementedError

    @abstractmethod
    def get_daily_stock_prices(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        period: str,
        adjusted_price: bool,
    ):
        raise NotImplementedError
