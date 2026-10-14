from stock.domain.market import TreasuryYieldMaturity
from stock.domain.port.domestic_market_index_client import DomesticMarketIndexClient
from stock.domain.port.fear_greed_client import FearGreedClient
from stock.domain.port.korea_stock_list_client import KoreaStockListClient
from stock.domain.port.overseas_market_index_client import OverseasMarketIndexClient
from stock.domain.port.vix_client import VixClient
from stock.domain.port.vkospi_client import VkospiClient


TREASURY_YIELD_CODES = {
    TreasuryYieldMaturity.KOREA_1Y: "Y0104",
    TreasuryYieldMaturity.KOREA_3Y: "Y0101",
    TreasuryYieldMaturity.KOREA_5Y: "Y0105",
    TreasuryYieldMaturity.KOREA_10Y: "Y0106",
    TreasuryYieldMaturity.US_1Y: "Y0203",
    TreasuryYieldMaturity.US_10Y: "Y0202",
}


class MarketIndexService:
    """각 시장 지표를 소유 포트에 연결하고 KIS 코드 매핑을 제공한다."""

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

    def get_usd_krw_exchange_rate(self, start_date: str, end_date: str):
        """KIS 해외 지수 API에서 USD/KRW 환율을 조회한다."""

        return self.overseas_market_client.get_overseas_market_index_prices(
            "X", "FX@KRW", start_date, end_date
        )

    def get_treasury_yield(
        self,
        maturity: TreasuryYieldMaturity,
        start_date: str,
        end_date: str,
    ):
        """국가와 만기에 해당하는 KIS 국채 시계열 코드를 선택해 조회한다."""

        code = TREASURY_YIELD_CODES[maturity]
        return self.overseas_market_client.get_overseas_market_index_prices(
            "I", code, start_date, end_date
        )

    def get_sp500_index(self, start_date: str, end_date: str):
        """KIS 해외 지수 API에서 S&P 500 지수를 조회한다."""

        return self.overseas_market_client.get_overseas_market_index_prices(
            "N", "SPX", start_date, end_date
        )

    def get_kospi_index(self, start_date: str, end_date: str):
        """KIS 국내 지수 API에서 KOSPI를 조회한다."""

        return self.domestic_market_client.get_domestic_market_index_prices(
            "U", "0001", start_date, end_date
        )

    def get_kosdaq_index(self, start_date: str, end_date: str):
        """KIS 국내 지수 API에서 KOSDAQ을 조회한다."""

        return self.domestic_market_client.get_domestic_market_index_prices(
            "U", "1001", start_date, end_date
        )
