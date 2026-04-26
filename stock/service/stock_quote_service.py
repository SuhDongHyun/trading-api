from stock.domain.adapter.api_client import IApiClient


class StockQuoteService:
    def __init__(self, api_client: IApiClient):
        self.api_client = api_client

    def get_stock_info(self, market: str, code: str):
        return self.api_client.get_stock_info(market, code)

    def get_daily_stock_prices(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        period: str,
        adjusted_price: bool = True,
    ):
        return self.api_client.get_daily_stock_prices(
            market=market,
            code=code,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjusted_price=adjusted_price,
        )
