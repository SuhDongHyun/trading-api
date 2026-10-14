from dependency_injector import containers, providers

from config import settings
from stock.infra.cnn.fear_greed_client import CnnFearGreedClient
from stock.infra.fred.fred_client import FredClient
from stock.infra.kis.kis_account_client import KisAccountClient
from stock.infra.kis.kis_domestic_market_index_client import (
    KisDomesticMarketIndexClient,
)
from stock.infra.kis.kis_http_client import KisHttpClient
from stock.infra.kis.kis_news_client import KisNewsClient
from stock.infra.kis.kis_overseas_market_index_client import (
    KisOverseasMarketIndexClient,
)
from stock.infra.kis.kis_rate_limiter import KisRateLimiter
from stock.infra.kis.kis_stock_quote_client import KisStockQuoteClient
from stock.infra.kis.kis_token_manager import KisTokenManager
from stock.infra.krx.krx_client import KRXClient
from stock.service.account_service import AccountService
from stock.service.market_index_service import MarketIndexService
from stock.service.stock_news_service import StockNewsService
from stock.service.stock_quote_service import StockQuoteService


class Container(containers.DeclarativeContainer):
    """공유 KIS 전송 구성요소와 요청별 어댑터·서비스를 묶는다."""

    wiring_config = containers.WiringConfiguration(
        packages=["stock.interface.controller"]
    )

    kis_settings = providers.Object(settings.kis)
    kis_token_manager = providers.Singleton(KisTokenManager, kis_settings=kis_settings)
    kis_rate_limiter = providers.Singleton(KisRateLimiter)
    kis_http_client = providers.Singleton(
        KisHttpClient,
        kis_settings=kis_settings,
        token_manager=kis_token_manager,
        rate_limiter=kis_rate_limiter,
    )

    kis_account_client = providers.Factory(
        KisAccountClient, http_client=kis_http_client, kis_settings=kis_settings
    )
    kis_stock_quote_client = providers.Factory(
        KisStockQuoteClient, http_client=kis_http_client
    )
    kis_news_client = providers.Factory(KisNewsClient, http_client=kis_http_client)
    kis_domestic_market_index_client = providers.Factory(
        KisDomesticMarketIndexClient, http_client=kis_http_client
    )
    kis_overseas_market_index_client = providers.Factory(
        KisOverseasMarketIndexClient, http_client=kis_http_client
    )

    fred_client = providers.Factory(FredClient, api_key=settings.fred.api_key)
    fear_greed_client = providers.Factory(CnnFearGreedClient)
    krx_client = providers.Singleton(KRXClient, api_key=settings.krx.api_key)

    account_service = providers.Factory(
        AccountService, account_client=kis_account_client
    )
    stock_news_service = providers.Factory(
        StockNewsService, news_client=kis_news_client
    )
    stock_quote_service = providers.Factory(
        StockQuoteService, quote_client=kis_stock_quote_client
    )
    market_index_service = providers.Factory(
        MarketIndexService,
        domestic_market_client=kis_domestic_market_index_client,
        overseas_market_client=kis_overseas_market_index_client,
        stock_list_client=krx_client,
        vkospi_client=krx_client,
        vix_client=fred_client,
        fear_greed_client=fear_greed_client,
    )
