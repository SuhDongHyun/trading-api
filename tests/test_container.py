import main


def test_kis_transports_are_shared_across_all_adapters():
    """토큰과 appkey rate limit이 모든 KIS 어댑터에서 공유되는지 보장한다."""

    container = main.container
    account_service = container.account_service()
    quote_service = container.stock_quote_service()
    news_service = container.stock_news_service()
    market_service = container.market_index_service()

    kis_adapters = [
        account_service.account_client,
        quote_service.quote_client,
        news_service.news_client,
        market_service.domestic_market_client,
        market_service.overseas_market_client,
    ]
    http_client = container.kis_http_client()

    assert all(adapter._http_client is http_client for adapter in kis_adapters)
    assert http_client._token_manager is container.kis_token_manager()
    assert http_client._rate_limiter is container.kis_rate_limiter()
    assert market_service.stock_list_client is container.krx_client()
    assert market_service.vkospi_client is container.krx_client()


def test_upbit_transport_and_limiter_are_shared_across_adapters():
    """Upbit 공개 API client와 그룹별 limiter는 singleton으로 공유한다."""

    container = main.container
    http_client = container.upbit_http_client()

    service_adapters = [
        container.trading_pair_service()._trading_pair_client,
        container.ticker_service()._ticker_client,
        container.quote_ticker_service()._ticker_client,
        container.orderbook_service()._orderbook_client,
        container.orderbook_instrument_service()._instrument_client,
        container.trade_service()._trade_client,
    ]
    assert all(adapter._http_client is http_client for adapter in service_adapters)
    assert all(
        adapter._http_client is http_client
        for adapter in (
            container.upbit_trading_pair_client(),
            container.upbit_ticker_client(),
            container.upbit_quote_ticker_client(),
            container.upbit_orderbook_client(),
            container.upbit_orderbook_instrument_client(),
            container.upbit_trade_client(),
        )
    )
    assert http_client._rate_limiter is container.upbit_rate_limiter()
