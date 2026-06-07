from dependency_injector import containers, providers

from stock.infra.kis.kis_client import KISClient
from stock.infra.fred.fred_client import FredClient
from stock.service.account_service import AccountService
from stock.service.stock_news_service import StockNewsService
from stock.service.stock_quote_service import StockQuoteService
from stock.service.market_indicator_service import MarketIndicatorService


class Container(containers.DeclarativeContainer):
    """FastAPI 컨트롤러에 주입할 클라이언트와 서비스 객체를 구성한다."""

    wiring_config = containers.WiringConfiguration(
        packages=["stock.interface.controller"]
    )

    kis_client = providers.Factory(KISClient)
    fred_client = providers.Factory(FredClient)
    account_service = providers.Factory(AccountService, api_client=kis_client)
    stock_news_service = providers.Factory(StockNewsService, api_client=kis_client)
    stock_quote_service = providers.Factory(StockQuoteService, api_client=kis_client)
    market_indicator_service = providers.Factory(
        MarketIndicatorService, market_client=fred_client, api_client=kis_client
    )
