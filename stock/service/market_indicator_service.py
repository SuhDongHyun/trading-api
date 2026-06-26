from stock.domain.adapter.market_client import IMarketClient
from stock.domain.adapter.api_client import IApiClient
from stock.service.indicator.common import resolve_base_indicator_date_range


TREASURY_YIELD_CODES = {
    ("KR", "1Y"): "Y0104",
    ("KR", "3Y"): "Y0101",
    ("KR", "5Y"): "Y0105",
    ("KR", "10Y"): "Y0106",
    ("US", "1Y"): "Y0203",
    ("US", "10Y"): "Y0202",
}


class MarketIndicatorService:
    """시장 지표 관련 비즈니스 로직을 담당하는 서비스 클래스."""

    def __init__(self, market_client: IMarketClient, api_client: IApiClient):
        """시장 지표 데이터를 가져올 시장 클라이언트를 주입받는다."""

        self.market_client = market_client
        self.api_client = api_client

    def get_fear_and_greed_index(self):
        """현재 시장의 공포탐욕지수를 조회한다."""

        return self.market_client.get_fear_and_greed_index()

    def get_vix_index(self, start_date: str, end_date: str):
        """현재 시장의 VIX 지수를 조회한다."""

        return self.market_client.get_vix_index(start_date, end_date)

    def get_usd_krw_exchange_rate(self, start_date: str, end_date: str, period: str):
        """현재 시장의 USD/KRW 환율을 조회한다."""

        return self._get_overseas_market_indicator_prices(
            "X", "FX@KRW", start_date, end_date, period
        )

    def _get_domestic_market_indicator_prices(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        period: str,
    ):
        """조회 기간을 보정한 뒤 시장 지표 가격을 조회한다."""

        valid_start_date, valid_end_date = resolve_base_indicator_date_range(
            start_date, end_date, period
        )

        return self.api_client.get_domestic_market_indicator_prices(
            market, code, valid_start_date, valid_end_date, period
        )

    def _get_overseas_market_indicator_prices(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        period: str,
    ):
        """조회 기간을 보정한 뒤 시장 지표 가격을 조회한다."""

        valid_start_date, valid_end_date = resolve_base_indicator_date_range(
            start_date, end_date, period
        )

        return self.api_client.get_overseas_market_indicator_prices(
            market, code, valid_start_date, valid_end_date, period
        )

    def get_treasury_yield(
        self,
        country: str,
        maturity: str,
        start_date: str,
        end_date: str,
    ):
        """국가와 만기로 국채 수익률을 조회한다."""

        code = TREASURY_YIELD_CODES[(country, maturity)]
        return self._get_overseas_market_indicator_prices(
            "I", code, start_date, end_date, "D"
        )

    def get_korea_1y_treasury_yield(self, start_date: str, end_date: str):
        """현재 시장의 한국 1년 만기 국채 수익률을 조회한다."""

        return self.get_treasury_yield("KR", "1Y", start_date, end_date)

    def get_korea_3y_treasury_yield(self, start_date: str, end_date: str):
        """현재 시장의 한국 3년 만기 국채 수익률을 조회한다."""

        return self.get_treasury_yield("KR", "3Y", start_date, end_date)

    def get_korea_5y_treasury_yield(self, start_date: str, end_date: str):
        """현재 시장의 한국 5년 만기 국채 수익률을 조회한다."""

        return self.get_treasury_yield("KR", "5Y", start_date, end_date)

    def get_korea_10y_treasury_yield(self, start_date: str, end_date: str):
        """현재 시장의 한국 10년 만기 국채 수익률을 조회한다."""

        return self.get_treasury_yield("KR", "10Y", start_date, end_date)

    def get_us_1y_treasury_yield(self, start_date: str, end_date: str):
        """현재 시장의 미국 1년 만기 국채 수익률을 조회한다."""

        return self.get_treasury_yield("US", "1Y", start_date, end_date)

    def get_us_10y_treasury_yield(self, start_date: str, end_date: str):
        """현재 시장의 미국 10년 만기 국채 수익률을 조회한다."""

        return self.get_treasury_yield("US", "10Y", start_date, end_date)

    def get_sp500_index(self, start_date: str, end_date: str):
        """현재 시장의 S&P 500 지수를 조회한다."""

        return self._get_overseas_market_indicator_prices(
            "N", "SPX", start_date, end_date, "D"
        )

    def get_kospi_index(self, start_date: str, end_date: str):
        """현재 시장의 KOSPI 지수를 조회한다."""

        return self._get_domestic_market_indicator_prices(
            "U", "0001", start_date, end_date, "D"
        )

    def get_kosdaq_index(self, start_date: str, end_date: str):
        """현재 시장의 KOSDAQ 지수를 조회한다."""

        return self._get_domestic_market_indicator_prices(
            "U", "1001", start_date, end_date, "D"
        )
