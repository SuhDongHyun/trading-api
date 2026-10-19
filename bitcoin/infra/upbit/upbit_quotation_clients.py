from collections.abc import Sequence

from bitcoin.domain.port.quotation_clients import (
    OrderbookClient,
    OrderbookInstrumentClient,
    QuoteTickerClient,
    TickerClient,
    TradeClient,
    TradingPairClient,
)
from bitcoin.domain.quotation import (
    MarketEvent,
    MarketEventCaution,
    Orderbook,
    OrderbookInstrument,
    OrderbookUnit,
    Ticker,
    Trade,
    TradingPair,
)
from bitcoin.infra.upbit.upbit_http_client import UpbitHttpClient


def _ticker_from_response(body: dict) -> Ticker:
    """Upbit ticker 객체의 공식 필드를 도메인 모델로 바꾼다."""

    return Ticker(**{field: body[field] for field in Ticker.__dataclass_fields__})


class UpbitTradingPairClient(TradingPairClient):
    """페어 목록 API 어댑터."""

    def __init__(self, http_client: UpbitHttpClient):
        self._http_client = http_client

    def get_trading_pairs(self, is_details: bool = False) -> list[TradingPair]:
        response = self._http_client.get(
            "/v1/market/all",
            params={"is_details": "true" if is_details else "false"},
            rate_limit_group="market",
        )
        result = []
        for item in response.json():
            event_data = item.get("market_event")
            event = None
            if isinstance(event_data, dict):
                caution_data = event_data.get("caution") or {}
                event = MarketEvent(
                    warning=event_data["warning"],
                    caution=MarketEventCaution(
                        PRICE_FLUCTUATIONS=caution_data.get(
                            "PRICE_FLUCTUATIONS", False
                        ),
                        TRADING_VOLUME_SOARING=caution_data.get(
                            "TRADING_VOLUME_SOARING", False
                        ),
                        DEPOSIT_AMOUNT_SOARING=caution_data.get(
                            "DEPOSIT_AMOUNT_SOARING", False
                        ),
                        GLOBAL_PRICE_DIFFERENCES=caution_data.get(
                            "GLOBAL_PRICE_DIFFERENCES", False
                        ),
                        CONCENTRATION_OF_SMALL_ACCOUNTS=caution_data.get(
                            "CONCENTRATION_OF_SMALL_ACCOUNTS", False
                        ),
                    ),
                )
            result.append(
                TradingPair(
                    market=item["market"],
                    korean_name=item["korean_name"],
                    english_name=item["english_name"],
                    market_warning=item.get("market_warning"),
                    market_event=event,
                )
            )
        return result


class UpbitTickerClient(TickerClient):
    """페어 단위 현재가 API 어댑터."""

    def __init__(self, http_client: UpbitHttpClient):
        self._http_client = http_client

    def get_tickers(self, markets: list[str]) -> list[Ticker]:
        response = self._http_client.get(
            "/v1/ticker",
            params={"markets": ",".join(markets)},
            rate_limit_group="ticker",
        )
        return [_ticker_from_response(item) for item in response.json()]


class UpbitQuoteTickerClient(QuoteTickerClient):
    """호가 통화 단위 현재가 API 어댑터."""

    def __init__(self, http_client: UpbitHttpClient):
        self._http_client = http_client

    def get_tickers(self, quote_currencies: Sequence[str]) -> list[Ticker]:
        response = self._http_client.get(
            "/v1/ticker/all",
            params={"quote_currencies": ",".join(quote_currencies)},
            rate_limit_group="ticker",
        )
        return [_ticker_from_response(item) for item in response.json()]


class UpbitOrderbookClient(OrderbookClient):
    """호가 API 어댑터."""

    def __init__(self, http_client: UpbitHttpClient):
        self._http_client = http_client

    def get_orderbooks(
        self, markets: list[str], level: str = "0", count: int = 30
    ) -> list[Orderbook]:
        response = self._http_client.get(
            "/v1/orderbook",
            params={"markets": ",".join(markets), "level": level, "count": count},
            rate_limit_group="orderbook",
        )
        return [
            Orderbook(
                market=item["market"],
                timestamp=item["timestamp"],
                total_ask_size=item["total_ask_size"],
                total_bid_size=item["total_bid_size"],
                level=item["level"],
                orderbook_units=[
                    OrderbookUnit(
                        ask_price=unit["ask_price"],
                        bid_price=unit["bid_price"],
                        ask_size=unit["ask_size"],
                        bid_size=unit["bid_size"],
                    )
                    for unit in item["orderbook_units"]
                ],
            )
            for item in response.json()
        ]


class UpbitOrderbookInstrumentClient(OrderbookInstrumentClient):
    """호가 정책 API 어댑터."""

    def __init__(self, http_client: UpbitHttpClient):
        self._http_client = http_client

    def get_orderbook_instruments(
        self, markets: list[str]
    ) -> list[OrderbookInstrument]:
        response = self._http_client.get(
            "/v1/orderbook/instruments",
            params={"markets": ",".join(markets)},
            rate_limit_group="orderbook",
        )
        return [
            OrderbookInstrument(
                **{
                    field: item[field]
                    for field in OrderbookInstrument.__dataclass_fields__
                }
            )
            for item in response.json()
        ]


class UpbitTradeClient(TradeClient):
    """최근 체결 내역 API 어댑터."""

    def __init__(self, http_client: UpbitHttpClient):
        self._http_client = http_client

    def get_trades(
        self,
        market: str,
        to: str | None = None,
        count: int = 1,
        cursor: str | None = None,
        days_ago: int | None = None,
    ) -> list[Trade]:
        params: dict[str, str | int] = {"market": market, "count": count}
        if to is not None:
            params["to"] = to
        if cursor is not None:
            params["cursor"] = cursor
        if days_ago is not None:
            params["days_ago"] = days_ago

        response = self._http_client.get(
            "/v1/trades/ticks", params=params, rate_limit_group="trade"
        )
        return [
            Trade(**{field: item[field] for field in Trade.__dataclass_fields__})
            for item in response.json()
        ]
