from abc import ABC, abstractmethod


class ICompositeIndexClient(ABC):
    """국내외 시장 지수 정보를 제공하는 통합 포트."""

    @abstractmethod
    def get_fear_and_greed_index(self):
        raise NotImplementedError

    @abstractmethod
    def get_vix_index(self, start_date: str, end_date: str):
        raise NotImplementedError

    @abstractmethod
    def get_vkospi_index(self, start_date: str, end_date: str):
        raise NotImplementedError

    @abstractmethod
    def get_usd_krw_exchange_rate(self, start_date: str, end_date: str, period: str):
        raise NotImplementedError

    @abstractmethod
    def get_treasury_yield(self, code, start_date: str, end_date: str):
        raise NotImplementedError

    @abstractmethod
    def get_sp500_index(self, start_date: str, end_date: str):
        raise NotImplementedError

    @abstractmethod
    def get_kospi_index(self, start_date: str, end_date: str):
        raise NotImplementedError

    @abstractmethod
    def get_kosdaq_index(self, start_date: str, end_date: str):
        raise NotImplementedError
