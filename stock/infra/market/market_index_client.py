from stock.domain.adapter.composite_index_client import ICompositeIndexClient
from stock.domain.adapter.api_client import IApiClient
from stock.domain.adapter.domestic_index_client import IDomesticIndexClient
from stock.domain.adapter.overseas_index_client import IOverseasIndexClient


class MarketIndexClient(ICompositeIndexClient):
    """국내외 시장 지수 정보를 제공하는 통합 포트 구현체."""

    def __init__(
        self,
        api_client: IApiClient,
        overseas_client: IOverseasIndexClient,
        domestic_client: IDomesticIndexClient,
    ):
        self.api_client = api_client
        self.overseas_client = overseas_client
        self.domestic_client = domestic_client

    def get_korea_stock_list(self):
        """KRX 상장 종목 리스트를 조회한다."""

        return self.domestic_client.get_korea_stock_list()

    def get_fear_and_greed_index(self):
        """현재 시장의 공포탐욕지수를 조회한다."""

        return self.overseas_client.get_fear_and_greed_index()

    def get_vix_index(self, start_date: str, end_date: str):
        """현재 시장의 VIX 지수를 조회한다."""

        return self.overseas_client.get_vix_index(start_date, end_date)

    def get_vkospi_index(self, start_date: str, end_date: str):
        """국내 시장의 VKOSPI 지수를 조회한다."""

        return self.domestic_client.get_vkospi_index(start_date, end_date)

    def get_usd_krw_exchange_rate(self, start_date: str, end_date: str):
        """현재 시장의 USD/KRW 환율을 조회한다."""

        return self.api_client.get_overseas_market_index_prices(
            "X", "FX@KRW", start_date, end_date, "D"
        )

    def get_treasury_yield(self, code, start_date: str, end_date: str):
        """현재 시장의 국채 수익률을 조회한다."""

        return self.api_client.get_overseas_market_index_prices(
            "I", code, start_date, end_date, "D"
        )

    def get_sp500_index(self, start_date: str, end_date: str):
        """현재 시장의 S&P 500 지수를 조회한다."""

        return self.api_client.get_overseas_market_index_prices(
            "N", "SPX", start_date, end_date, "D"
        )

    def get_kospi_index(self, start_date: str, end_date: str):
        """현재 시장의 KOSPI 지수를 조회한다."""

        return self.api_client.get_domestic_market_index_prices(
            "U", "0001", start_date, end_date, "D"
        )

    def get_kosdaq_index(self, start_date: str, end_date: str):
        """현재 시장의 KOSDAQ 지수를 조회한다."""

        return self.api_client.get_domestic_market_index_prices(
            "U", "1001", start_date, end_date, "D"
        )
