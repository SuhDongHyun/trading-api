from dependency_injector import containers, providers

from config import settings
from bitcoin.infra.upbit.upbit_http_client import UpbitHttpClient
from bitcoin.infra.upbit.upbit_quotation_clients import (
    UpbitCandleClient,
    UpbitOrderbookClient,
    UpbitOrderbookInstrumentClient,
    UpbitQuoteTickerClient,
    UpbitTickerClient,
    UpbitTradingPairClient,
    UpbitTradeClient,
)
from bitcoin.infra.upbit.upbit_rate_limiter import UpbitRateLimiter
from bitcoin.service.quotation_services import (
    CandleService,
    OrderbookInstrumentService,
    OrderbookService,
    QuoteTickerService,
    TickerService,
    TradingPairService,
    TradeService,
)
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
        packages=["stock.interface.controller", "bitcoin.interface.controller"]
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

    upbit_settings = providers.Object(settings.upbit)
    upbit_rate_limiter = providers.Singleton(UpbitRateLimiter)
    upbit_http_client = providers.Singleton(
        UpbitHttpClient,
        upbit_settings=upbit_settings,
        rate_limiter=upbit_rate_limiter,
    )

    upbit_trading_pair_client = providers.Factory(
        UpbitTradingPairClient, http_client=upbit_http_client
    )
    upbit_ticker_client = providers.Factory(
        UpbitTickerClient, http_client=upbit_http_client
    )
    upbit_quote_ticker_client = providers.Factory(
        UpbitQuoteTickerClient, http_client=upbit_http_client
    )
    upbit_orderbook_client = providers.Factory(
        UpbitOrderbookClient, http_client=upbit_http_client
    )
    upbit_orderbook_instrument_client = providers.Factory(
        UpbitOrderbookInstrumentClient, http_client=upbit_http_client
    )
    upbit_trade_client = providers.Factory(
        UpbitTradeClient, http_client=upbit_http_client
    )
    upbit_candle_client = providers.Factory(
        UpbitCandleClient, http_client=upbit_http_client
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
    trading_pair_service = providers.Factory(
        TradingPairService, trading_pair_client=upbit_trading_pair_client
    )
    ticker_service = providers.Factory(TickerService, ticker_client=upbit_ticker_client)
    quote_ticker_service = providers.Factory(
        QuoteTickerService, ticker_client=upbit_quote_ticker_client
    )
    orderbook_service = providers.Factory(
        OrderbookService, orderbook_client=upbit_orderbook_client
    )
    orderbook_instrument_service = providers.Factory(
        OrderbookInstrumentService,
        instrument_client=upbit_orderbook_instrument_client,
    )
    trade_service = providers.Factory(TradeService, trade_client=upbit_trade_client)
    candle_service = providers.Factory(CandleService, candle_client=upbit_candle_client)
    market_index_service = providers.Factory(
        MarketIndexService,
        domestic_market_client=kis_domestic_market_index_client,
        overseas_market_client=kis_overseas_market_index_client,
        stock_list_client=krx_client,
        vkospi_client=krx_client,
        vix_client=fred_client,
        fear_greed_client=fear_greed_client,
    )
