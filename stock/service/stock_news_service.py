from stock.domain.adapter.api_client import IApiClient


class StockNewsService:
    def __init__(self, api_client: IApiClient):
        self.api_client = api_client

    def get_total_news(
        self,
        code: str,
        search_date: str,
        search_time: str,
    ):
        return self.api_client.get_total_news(code, search_date, search_time)
