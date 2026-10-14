from stock.domain.port.domestic_market_index_client import DomesticMarketIndexClient
from stock.domain.port.fear_greed_client import FearGreedClient
from stock.domain.port.korea_stock_list_client import KoreaStockListClient
from stock.domain.port.overseas_market_index_client import OverseasMarketIndexClient
from stock.domain.port.vix_client import VixClient
from stock.domain.port.vkospi_client import VkospiClient


MARKET_INDEX_CODES = {
    "usd_krw": ("overseas", "X", "FX@KRW"),
    "korea_1y_treasury": ("overseas", "I", "Y0104"),
    "korea_3y_treasury": ("overseas", "I", "Y0101"),
    "korea_5y_treasury": ("overseas", "I", "Y0105"),
    "korea_10y_treasury": ("overseas", "I", "Y0106"),
    "us_1y_treasury": ("overseas", "I", "Y0203"),
    "us_10y_treasury": ("overseas", "I", "Y0202"),
    "sp500": ("overseas", "N", "SPX"),
    "kospi": ("domestic", "U", "0001"),
    "kosdaq": ("domestic", "U", "1001"),
}


class MarketIndexService:
    """각 시장 지표의 조회 역할을 조합하고 KIS 코드 매핑을 담당한다."""

    def __init__(
        self,
        domestic_market_client: DomesticMarketIndexClient,
        overseas_market_client: OverseasMarketIndexClient,
        stock_list_client: KoreaStockListClient,
        vkospi_client: VkospiClient,
        vix_client: VixClient,
        fear_greed_client: FearGreedClient,
    ):
        self.domestic_market_client = domestic_market_client
        self.overseas_market_client = overseas_market_client
        self.stock_list_client = stock_list_client
        self.vkospi_client = vkospi_client
        self.vix_client = vix_client
        self.fear_greed_client = fear_greed_client

    def get_korea_stock_list(self):
        """KRX 상장 종목 리스트를 조회한다."""

        return self.stock_list_client.get_korea_stock_list()

    def get_fear_and_greed_index(self):
        """CNN 공포탐욕지수를 조회한다."""

        return self.fear_greed_client.get_fear_and_greed_index()

    def get_vix_index(self, start_date: str, end_date: str):
        """FRED에서 지정 구간의 VIX를 조회한다."""

        return self.vix_client.get_vix_index(start_date, end_date)

    def get_vkospi_index(self, start_date: str, end_date: str):
        """KRX에서 지정 구간의 VKOSPI를 조회한다."""

        return self.vkospi_client.get_vkospi_index(start_date, end_date)

    def _get_market_index_prices(self, key: str, start_date: str, end_date: str):
        source, market, code = MARKET_INDEX_CODES[key]
        client = (
            self.domestic_market_client
            if source == "domestic"
            else self.overseas_market_client
        )
        method = (
            client.get_domestic_market_index_prices
            if source == "domestic"
            else client.get_overseas_market_index_prices
        )
        return method(market, code, start_date, end_date)

    def get_usd_krw_exchange_rate(self, start_date: str, end_date: str):
        """KIS 해외 지수 API에서 USD/KRW 환율을 조회한다."""

        return self._get_market_index_prices("usd_krw", start_date, end_date)

    def get_korea_1y_treasury_yield(self, start_date: str, end_date: str):
        """한국 1년 만기 국채 수익률을 조회한다."""

        return self._get_market_index_prices("korea_1y_treasury", start_date, end_date)

    def get_korea_3y_treasury_yield(self, start_date: str, end_date: str):
        """한국 3년 만기 국채 수익률을 조회한다."""

        return self._get_market_index_prices("korea_3y_treasury", start_date, end_date)

    def get_korea_5y_treasury_yield(self, start_date: str, end_date: str):
        """한국 5년 만기 국채 수익률을 조회한다."""

        return self._get_market_index_prices("korea_5y_treasury", start_date, end_date)

    def get_korea_10y_treasury_yield(self, start_date: str, end_date: str):
        """한국 10년 만기 국채 수익률을 조회한다."""

        return self._get_market_index_prices("korea_10y_treasury", start_date, end_date)

    def get_us_1y_treasury_yield(self, start_date: str, end_date: str):
        """미국 1년 만기 국채 수익률을 조회한다."""

        return self._get_market_index_prices("us_1y_treasury", start_date, end_date)

    def get_us_10y_treasury_yield(self, start_date: str, end_date: str):
        """미국 10년 만기 국채 수익률을 조회한다."""

        return self._get_market_index_prices("us_10y_treasury", start_date, end_date)

    def get_sp500_index(self, start_date: str, end_date: str):
        """KIS 해외 지수 API에서 S&P 500 지수를 조회한다."""

        return self._get_market_index_prices("sp500", start_date, end_date)

    def get_kospi_index(self, start_date: str, end_date: str):
        """KIS 국내 지수 API에서 KOSPI를 조회한다."""

        return self._get_market_index_prices("kospi", start_date, end_date)

    def get_kosdaq_index(self, start_date: str, end_date: str):
        """KIS 국내 지수 API에서 KOSDAQ을 조회한다."""

        return self._get_market_index_prices("kosdaq", start_date, end_date)
