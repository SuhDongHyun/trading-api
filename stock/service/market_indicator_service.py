from stock.domain.adapter.market_client import IMarketClient


class MarketIndicatorService:
    """시장 지표 관련 비즈니스 로직을 담당하는 서비스 클래스."""

    def __init__(self, market_client: IMarketClient):
        """시장 지표 데이터를 가져올 시장 클라이언트를 주입받는다."""

        self.market_client = market_client

    def get_fear_and_greed_index(self):
        """현재 시장의 공포탐욕지수를 조회한다."""

        return self.market_client.get_fear_and_greed_index()

    def get_vix_index(self, start_date: str, end_date: str):
        """현재 시장의 VIX 지수를 조회한다."""

        return self.market_client.get_vix_index(start_date, end_date)
