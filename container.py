from dependency_injector import containers, providers

from stock.infra.kis.kis_client import KISClient
from stock.infra.fred.fred_client import FredClient
from stock.infra.krx.krx_client import KRXClient
from stock.infra.market.market_index_client import MarketIndexClient
from stock.service.account_service import AccountService
from stock.service.stock_news_service import StockNewsService
from stock.service.stock_quote_service import StockQuoteService
from stock.service.market_index_service import MarketIndexService


class Container(containers.DeclarativeContainer):
    """FastAPI 컨트롤러에 주입할 클라이언트와 서비스 객체를 구성한다."""

    wiring_config = containers.WiringConfiguration(
        packages=["stock.interface.controller"]
    )

    kis_client = providers.Factory(KISClient)
    fred_client = providers.Factory(FredClient)
    krx_client = providers.Factory(KRXClient)
    market_index_client = providers.Factory(
        MarketIndexClient,
        api_client=kis_client,
        overseas_client=fred_client,
        domestic_client=krx_client,
    )
    account_service = providers.Factory(AccountService, api_client=kis_client)
    stock_news_service = providers.Factory(StockNewsService, api_client=kis_client)
    stock_quote_service = providers.Factory(StockQuoteService, api_client=kis_client)
    market_index_service = providers.Factory(
        MarketIndexService, market_client=market_index_client
    )
