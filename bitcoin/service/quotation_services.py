from collections.abc import Sequence

from bitcoin.domain.port.quotation_clients import (
    OrderbookClient,
    OrderbookInstrumentClient,
    QuoteTickerClient,
    TickerClient,
    TradeClient,
    TradingPairClient,
)


class TradingPairService:
    """페어 목록 조회 유스케이스."""

    def __init__(self, trading_pair_client: TradingPairClient):
        self._trading_pair_client = trading_pair_client

    def get_trading_pairs(self, is_details: bool = False):
        return self._trading_pair_client.get_trading_pairs(is_details)


class TickerService:
    """페어별 현재가 조회 유스케이스."""

    def __init__(self, ticker_client: TickerClient):
        self._ticker_client = ticker_client

    def get_tickers(self, markets: list[str]):
        return self._ticker_client.get_tickers(markets)


class QuoteTickerService:
    """마켓별 현재가 조회 유스케이스."""

    def __init__(self, ticker_client: QuoteTickerClient):
        self._ticker_client = ticker_client

    def get_tickers(self, quote_currencies: Sequence[str]):
        return self._ticker_client.get_tickers(quote_currencies)


class OrderbookService:
    """호가 조회 유스케이스."""

    def __init__(self, orderbook_client: OrderbookClient):
        self._orderbook_client = orderbook_client

    def get_orderbooks(self, markets: list[str], level: str = "0", count: int = 30):
        return self._orderbook_client.get_orderbooks(markets, level, count)


class OrderbookInstrumentService:
    """호가 정책 조회 유스케이스."""

    def __init__(self, instrument_client: OrderbookInstrumentClient):
        self._instrument_client = instrument_client

    def get_orderbook_instruments(self, markets: list[str]):
        return self._instrument_client.get_orderbook_instruments(markets)


class TradeService:
    """최근 체결 내역 조회 유스케이스."""

    def __init__(self, trade_client: TradeClient):
        self._trade_client = trade_client

    def get_trades(
        self,
        market: str,
        to: str | None = None,
        count: int = 1,
        cursor: str | None = None,
        days_ago: int | None = None,
    ):
        return self._trade_client.get_trades(market, to, count, cursor, days_ago)
