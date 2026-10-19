from unittest.mock import Mock
from typing import cast

from bitcoin.domain.quotation import (
    Candle,
    DayCandle,
    MarketEvent,
    MarketEventCaution,
    Orderbook,
    OrderbookInstrument,
    OrderbookUnit,
    MinuteCandle,
    PeriodCandle,
    Ticker,
    Trade,
    TradingPair,
)
from bitcoin.infra.upbit.upbit_quotation_clients import (
    UpbitCandleClient,
    UpbitOrderbookClient,
    UpbitOrderbookInstrumentClient,
    UpbitQuoteTickerClient,
    UpbitTickerClient,
    UpbitTradeClient,
    UpbitTradingPairClient,
)
from bitcoin.infra.upbit.upbit_http_client import UpbitHttpClient
from bitcoin.service.quotation_services import (
    CandleService,
    OrderbookInstrumentService,
    OrderbookService,
    QuoteTickerService,
    TickerService,
    TradeService,
    TradingPairService,
)


TICKER_BODY = {
    "market": "KRW-BTC",
    "trade_date": "20250704",
    "trade_time": "051400",
    "trade_date_kst": "20250704",
    "trade_time_kst": "141400",
    "trade_timestamp": 1751606040365,
    "opening_price": 148737000,
    "high_price": 149360000,
    "low_price": 148288000,
    "trade_price": 148601000,
    "prev_closing_price": 148737000,
    "change": "FALL",
    "change_price": 136000,
    "change_rate": 0.0009143656,
    "signed_change_price": -136000,
    "signed_change_rate": -0.0009143656,
    "trade_volume": 0.00016823,
    "acc_trade_price": 31615925234.05438,
    "acc_trade_price_24h": 178448329314.96686,
    "acc_trade_volume": 212.38911576,
    "acc_trade_volume_24h": 1198.26954807,
    "highest_52_week_price": 163325000,
    "highest_52_week_date": "2025-01-20",
    "lowest_52_week_price": 72100000,
    "lowest_52_week_date": "2024-08-05",
    "timestamp": 1751606040403,
}


class FakeResponse:
    def __init__(self, body):
        self._body = body

    def json(self):
        return self._body


class RecordingHttpClient:
    def __init__(self, body):
        self.body = body
        self.calls = []

    def get(self, path, params=None, rate_limit_group="market"):
        self.calls.append((path, params, rate_limit_group))
        return FakeResponse(self.body)


def http_client_double(client: RecordingHttpClient) -> UpbitHttpClient:
    """테스트용 기록기 응답을 어댑터의 HTTP client 타입으로 취급한다."""

    return cast(UpbitHttpClient, client)


def test_trading_pair_adapter_maps_optional_market_event():
    http = RecordingHttpClient(
        [
            {
                "market": "KRW-BTC",
                "korean_name": "비트코인",
                "english_name": "Bitcoin",
                "market_warning": "NONE",
                "market_event": {
                    "warning": False,
                    "caution": {
                        "PRICE_FLUCTUATIONS": False,
                        "TRADING_VOLUME_SOARING": True,
                        "DEPOSIT_AMOUNT_SOARING": False,
                        "GLOBAL_PRICE_DIFFERENCES": False,
                        "CONCENTRATION_OF_SMALL_ACCOUNTS": False,
                    },
                },
            }
        ]
    )

    values = UpbitTradingPairClient(http_client_double(http)).get_trading_pairs(
        is_details=True
    )

    assert values == [
        TradingPair(
            market="KRW-BTC",
            korean_name="비트코인",
            english_name="Bitcoin",
            market_warning="NONE",
            market_event=MarketEvent(
                warning=False,
                caution=MarketEventCaution(
                    PRICE_FLUCTUATIONS=False,
                    TRADING_VOLUME_SOARING=True,
                    DEPOSIT_AMOUNT_SOARING=False,
                    GLOBAL_PRICE_DIFFERENCES=False,
                    CONCENTRATION_OF_SMALL_ACCOUNTS=False,
                ),
            ),
        )
    ]
    assert http.calls == [("/v1/market/all", {"is_details": "true"}, "market")]


def test_ticker_adapters_share_ticker_group_and_comma_join_parameters():
    http = RecordingHttpClient([TICKER_BODY])

    ticker = UpbitTickerClient(http_client_double(http)).get_tickers(
        ["KRW-BTC", "KRW-ETH"]
    )
    quote_ticker = UpbitQuoteTickerClient(http_client_double(http)).get_tickers(
        ["KRW", "BTC"]
    )

    assert ticker == [Ticker(**TICKER_BODY)]
    assert quote_ticker == [Ticker(**TICKER_BODY)]
    assert http.calls == [
        ("/v1/ticker", {"markets": "KRW-BTC,KRW-ETH"}, "ticker"),
        ("/v1/ticker/all", {"quote_currencies": "KRW,BTC"}, "ticker"),
    ]


def test_orderbook_adapters_convert_units_and_use_orderbook_group():
    http = RecordingHttpClient(
        [
            {
                "market": "KRW-BTC",
                "timestamp": 1751606867762,
                "total_ask_size": 10.37591054,
                "total_bid_size": 9.49577219,
                "level": 10000,
                "orderbook_units": [
                    {
                        "ask_price": 148520000,
                        "bid_price": 148490000,
                        "ask_size": 0.0134662,
                        "bid_size": 0.04296774,
                    }
                ],
            }
        ]
    )

    values = UpbitOrderbookClient(http_client_double(http)).get_orderbooks(
        ["KRW-BTC"], level="10000", count=5
    )

    assert values == [
        Orderbook(
            market="KRW-BTC",
            timestamp=1751606867762,
            total_ask_size=10.37591054,
            total_bid_size=9.49577219,
            level=10000,
            orderbook_units=[
                OrderbookUnit(
                    ask_price=148520000,
                    bid_price=148490000,
                    ask_size=0.0134662,
                    bid_size=0.04296774,
                )
            ],
        )
    ]
    assert http.calls == [
        (
            "/v1/orderbook",
            {"markets": "KRW-BTC", "level": "10000", "count": 5},
            "orderbook",
        )
    ]

    http.body = [
        {
            "market": "KRW-BTC",
            "quote_currency": "KRW",
            "tick_size": "1000",
            "supported_levels": ["0", "10000"],
            "future_field": "ignored",
        }
    ]
    instruments = UpbitOrderbookInstrumentClient(
        http_client_double(http)
    ).get_orderbook_instruments(["KRW-BTC"])
    assert instruments == [
        OrderbookInstrument("KRW-BTC", "KRW", "1000", ["0", "10000"])
    ]
    assert http.calls[-1] == (
        "/v1/orderbook/instruments",
        {"markets": "KRW-BTC"},
        "orderbook",
    )


def test_trade_adapter_maps_cursor_and_optional_filters():
    body = {
        "market": "KRW-BTC",
        "trade_date_utc": "2025-06-27",
        "trade_time_utc": "23:59:59",
        "timestamp": 1751068799336,
        "trade_price": 147058000,
        "trade_volume": 0.00006043,
        "prev_closing_price": 146852000,
        "change_price": 206000,
        "ask_bid": "BID",
        "sequential_id": 17510687993360000,
        "future_field": "ignored",
    }
    http = RecordingHttpClient([body])

    values = UpbitTradeClient(http_client_double(http)).get_trades(
        "KRW-BTC",
        to="23:59:59",
        count=25,
        cursor="17510687993360000",
        days_ago=1,
    )

    assert values == [
        Trade(**{field: body[field] for field in Trade.__dataclass_fields__})
    ]
    assert http.calls == [
        (
            "/v1/trades/ticks",
            {
                "market": "KRW-BTC",
                "count": 25,
                "to": "23:59:59",
                "cursor": "17510687993360000",
                "days_ago": 1,
            },
            "trade",
        )
    ]


def test_quotation_services_forward_requests_to_role_ports():
    pair_client = Mock()
    ticker_client = Mock()
    quote_ticker_client = Mock()
    orderbook_client = Mock()
    instrument_client = Mock()
    trade_client = Mock()
    candle_client = Mock()

    TradingPairService(pair_client).get_trading_pairs(True)
    TickerService(ticker_client).get_tickers(["KRW-BTC"])
    QuoteTickerService(quote_ticker_client).get_tickers(["KRW"])
    OrderbookService(orderbook_client).get_orderbooks(["KRW-BTC"], "0", 30)
    OrderbookInstrumentService(instrument_client).get_orderbook_instruments(["KRW-BTC"])
    TradeService(trade_client).get_trades("KRW-BTC", count=2)
    candle_service = CandleService(candle_client)
    candle_service.get_seconds_candles("KRW-BTC", "2025-07-01T00:00:00Z", 2)
    candle_service.get_minute_candles(5, "KRW-BTC", "2025-07-01T00:00:00Z", 3)
    candle_service.get_day_candles("KRW-BTC", None, 4, "KRW")
    candle_service.get_week_candles("KRW-BTC", None, 5)
    candle_service.get_month_candles("KRW-BTC", None, 6)
    candle_service.get_year_candles("KRW-BTC", None, 7)

    pair_client.get_trading_pairs.assert_called_once_with(True)
    ticker_client.get_tickers.assert_called_once_with(["KRW-BTC"])
    quote_ticker_client.get_tickers.assert_called_once_with(["KRW"])
    orderbook_client.get_orderbooks.assert_called_once_with(["KRW-BTC"], "0", 30)
    instrument_client.get_orderbook_instruments.assert_called_once_with(["KRW-BTC"])
    trade_client.get_trades.assert_called_once_with("KRW-BTC", None, 2, None, None)
    candle_client.get_seconds_candles.assert_called_once_with(
        "KRW-BTC", "2025-07-01T00:00:00Z", 2
    )
    candle_client.get_minute_candles.assert_called_once_with(
        5, "KRW-BTC", "2025-07-01T00:00:00Z", 3
    )
    candle_client.get_day_candles.assert_called_once_with("KRW-BTC", None, 4, "KRW")
    candle_client.get_week_candles.assert_called_once_with("KRW-BTC", None, 5)
    candle_client.get_month_candles.assert_called_once_with("KRW-BTC", None, 6)
    candle_client.get_year_candles.assert_called_once_with("KRW-BTC", None, 7)


BASE_CANDLE_BODY = {
    "market": "KRW-BTC",
    "candle_date_time_utc": "2025-06-30T23:59:59",
    "candle_date_time_kst": "2025-07-01T08:59:59",
    "opening_price": 145794000,
    "high_price": 145794000,
    "low_price": 145759000,
    "trade_price": 145759000,
    "timestamp": 1751327999833,
    "candle_acc_trade_price": 185042,
    "candle_acc_trade_volume": 0.0013,
    "future_field": "ignored",
}


def test_candle_adapter_maps_each_upbit_shape_and_calls_once_per_request():
    http = RecordingHttpClient([BASE_CANDLE_BODY])
    client = UpbitCandleClient(http_client_double(http))

    seconds = client.get_seconds_candles("KRW-BTC", count=2)
    http.body = [{**BASE_CANDLE_BODY, "unit": 5}]
    minutes = client.get_minute_candles(
        5, "KRW-BTC", to="2025-07-01T00:00:00Z", count=3
    )
    http.body = [
        {
            **BASE_CANDLE_BODY,
            "prev_closing_price": 147996000,
            "change_price": -2237000,
            "change_rate": -0.0151152734,
            "converted_trade_price": 145759000,
        }
    ]
    days = client.get_day_candles("KRW-BTC", count=4, converting_price_unit="KRW")
    http.body = [{**BASE_CANDLE_BODY, "first_day_of_period": "2025-06-30"}]
    weeks = client.get_week_candles("KRW-BTC", count=5)
    months = client.get_month_candles("KRW-BTC", count=6)
    years = client.get_year_candles("KRW-BTC", count=7)

    base_candle = {
        field: value
        for field, value in BASE_CANDLE_BODY.items()
        if field != "future_field"
    }
    assert seconds == [Candle(**base_candle)]
    assert minutes == [MinuteCandle(**base_candle, unit=5)]
    assert days == [
        DayCandle(
            **base_candle,
            prev_closing_price=147996000,
            change_price=-2237000,
            change_rate=-0.0151152734,
            converted_trade_price=145759000,
        )
    ]
    period = PeriodCandle(**base_candle, first_day_of_period="2025-06-30")
    assert weeks == months == years == [period]
    assert http.calls == [
        ("/v1/candles/seconds", {"market": "KRW-BTC", "count": 2}, "candle"),
        (
            "/v1/candles/minutes/5",
            {
                "market": "KRW-BTC",
                "count": 3,
                "to": "2025-07-01T00:00:00Z",
            },
            "candle",
        ),
        (
            "/v1/candles/days",
            {
                "market": "KRW-BTC",
                "count": 4,
                "converting_price_unit": "KRW",
            },
            "candle",
        ),
        ("/v1/candles/weeks", {"market": "KRW-BTC", "count": 5}, "candle"),
        ("/v1/candles/months", {"market": "KRW-BTC", "count": 6}, "candle"),
        ("/v1/candles/years", {"market": "KRW-BTC", "count": 7}, "candle"),
    ]
