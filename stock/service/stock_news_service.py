from stock.domain.port.news_client import NewsClient


class StockNewsService:
    """종목 뉴스 조회 유스케이스를 처리하는 서비스."""

    def __init__(self, news_client: NewsClient):
        self.news_client = news_client

    def get_total_news(
        self,
        code: str,
        search_date: str,
        search_time: str,
    ):
        """지정 날짜의 지정 시간까지 발행된 종목 관련 뉴스를 모두 조회한다."""

        return self.news_client.get_total_news(code, search_date, search_time)
