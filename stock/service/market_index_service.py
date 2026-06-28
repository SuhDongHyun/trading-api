from stock.domain.adapter.composite_index_client import ICompositeIndexClient


TREASURY_YIELD_CODES = {
    ("KR", "1Y"): "Y0104",
    ("KR", "3Y"): "Y0101",
    ("KR", "5Y"): "Y0105",
    ("KR", "10Y"): "Y0106",
    ("US", "1Y"): "Y0203",
    ("US", "10Y"): "Y0202",
}


class MarketIndexService:
    """시장 지표 관련 비즈니스 로직을 담당하는 서비스 클래스."""

    def __init__(self, market_client: ICompositeIndexClient):
        """시장 지표 데이터를 가져올 시장 클라이언트를 주입받는다."""

        self.market_client = market_client

    def get_korea_stock_list(self):
        """KRX 상장 종목 리스트를 조회한다."""

        return self.market_client.get_korea_stock_list()

    def get_fear_and_greed_index(self):
        """현재 시장의 공포탐욕지수를 조회한다."""

        return self.market_client.get_fear_and_greed_index()

    def get_vix_index(self, start_date: str, end_date: str):
        """현재 시장의 VIX 지수를 조회한다."""

        return self.market_client.get_vix_index(start_date, end_date)

    def get_vkospi_index(self, start_date: str, end_date: str):
        """국내 시장의 VKOSPI 지수를 조회한다."""

        return self.market_client.get_vkospi_index(start_date, end_date)

    def get_usd_krw_exchange_rate(self, start_date: str, end_date: str):
        """현재 시장의 USD/KRW 환율을 조회한다."""

        return self.market_client.get_usd_krw_exchange_rate(start_date, end_date)

    def get_korea_1y_treasury_yield(self, start_date: str, end_date: str):
        """현재 시장의 한국 1년 만기 국채 수익률을 조회한다."""

        return self.market_client.get_treasury_yield(
            TREASURY_YIELD_CODES[("KR", "1Y")], start_date, end_date
        )

    def get_korea_3y_treasury_yield(self, start_date: str, end_date: str):
        """현재 시장의 한국 3년 만기 국채 수익률을 조회한다."""

        return self.market_client.get_treasury_yield(
            TREASURY_YIELD_CODES[("KR", "3Y")], start_date, end_date
        )

    def get_korea_5y_treasury_yield(self, start_date: str, end_date: str):
        """현재 시장의 한국 5년 만기 국채 수익률을 조회한다."""

        return self.market_client.get_treasury_yield(
            TREASURY_YIELD_CODES[("KR", "5Y")], start_date, end_date
        )

    def get_korea_10y_treasury_yield(self, start_date: str, end_date: str):
        """현재 시장의 한국 10년 만기 국채 수익률을 조회한다."""

        return self.market_client.get_treasury_yield(
            TREASURY_YIELD_CODES[("KR", "10Y")], start_date, end_date
        )

    def get_us_1y_treasury_yield(self, start_date: str, end_date: str):
        """현재 시장의 미국 1년 만기 국채 수익률을 조회한다."""

        return self.market_client.get_treasury_yield(
            TREASURY_YIELD_CODES[("US", "1Y")], start_date, end_date
        )

    def get_us_10y_treasury_yield(self, start_date: str, end_date: str):
        """현재 시장의 미국 10년 만기 국채 수익률을 조회한다."""

        return self.market_client.get_treasury_yield(
            TREASURY_YIELD_CODES[("US", "10Y")], start_date, end_date
        )

    def get_sp500_index(self, start_date: str, end_date: str):
        """현재 시장의 S&P 500 지수를 조회한다."""

        return self.market_client.get_sp500_index(start_date, end_date)

    def get_kospi_index(self, start_date: str, end_date: str):
        """현재 시장의 KOSPI 지수를 조회한다."""

        return self.market_client.get_kospi_index(start_date, end_date)

    def get_kosdaq_index(self, start_date: str, end_date: str):
        """현재 시장의 KOSDAQ 지수를 조회한다."""

        return self.market_client.get_kosdaq_index(start_date, end_date)
