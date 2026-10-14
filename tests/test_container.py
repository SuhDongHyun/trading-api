from container import Container


def test_kis_transports_are_shared_across_all_adapters():
    """토큰과 appkey rate limit이 모든 KIS 어댑터에서 공유되는지 보장한다."""

    container = Container()
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
