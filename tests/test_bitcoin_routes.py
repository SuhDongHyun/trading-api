from contextlib import ExitStack
from unittest.mock import Mock

from dependency_injector import providers
from fastapi.testclient import TestClient

import main
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


def make_ticker():
    return Ticker(
        market="KRW-BTC",
        trade_date="20250704",
        trade_time="051400",
        trade_date_kst="20250704",
        trade_time_kst="141400",
        trade_timestamp=1751606040365,
        opening_price=148737000,
        high_price=149360000,
        low_price=148288000,
        trade_price=148601000,
        prev_closing_price=148737000,
        change="FALL",
        change_price=136000,
        change_rate=0.0009143656,
        signed_change_price=-136000,
        signed_change_rate=-0.0009143656,
        trade_volume=0.00016823,
        acc_trade_price=31615925234.05438,
        acc_trade_price_24h=178448329314.96686,
        acc_trade_volume=212.38911576,
        acc_trade_volume_24h=1198.26954807,
        highest_52_week_price=163325000,
        highest_52_week_date="2025-01-20",
        lowest_52_week_price=72100000,
        lowest_52_week_date="2024-08-05",
        timestamp=1751606040403,
    )


def test_bitcoin_routes_validate_convert_and_call_all_six_services():
    services = {
        "trading_pair_service": Mock(),
        "ticker_service": Mock(),
        "quote_ticker_service": Mock(),
        "orderbook_service": Mock(),
        "orderbook_instrument_service": Mock(),
        "trade_service": Mock(),
    }
    services["trading_pair_service"].get_trading_pairs.return_value = [
        TradingPair(
            "KRW-BTC",
            "비트코인",
            "Bitcoin",
            market_event=MarketEvent(
                warning=False,
                caution=MarketEventCaution(False, False, False, False, False),
            ),
        )
    ]
    services["ticker_service"].get_tickers.return_value = [make_ticker()]
    services["quote_ticker_service"].get_tickers.return_value = [make_ticker()]
    services["orderbook_service"].get_orderbooks.return_value = [
        Orderbook(
            market="KRW-BTC",
            timestamp=1751606867762,
            total_ask_size=10.37591054,
            total_bid_size=9.49577219,
            level=10000,
            orderbook_units=[
                OrderbookUnit(148520000, 148490000, 0.0134662, 0.04296774)
            ],
        )
    ]
    services["orderbook_instrument_service"].get_orderbook_instruments.return_value = [
        OrderbookInstrument("KRW-BTC", "KRW", "1000", ["0", "10000"])
    ]
    services["trade_service"].get_trades.return_value = [
        Trade(
            "KRW-BTC",
            "2025-06-27",
            "23:59:59",
            1751068799336,
            147058000,
            0.00006043,
            146852000,
            206000,
            "BID",
            17510687993360000,
        )
    ]

    with ExitStack() as stack:
        for name, service in services.items():
            stack.enter_context(
                getattr(main.container, name).override(providers.Object(service))
            )
        with TestClient(main.app) as client:
            pairs = client.post("/bitcoin/trading-pairs", json={"is_details": True})
            ticker = client.post("/bitcoin/ticker", json={"markets": ["KRW-BTC"]})
            quote = client.post(
                "/bitcoin/ticker/quote", json={"quote_currencies": ["KRW"]}
            )
            orderbook = client.post(
                "/bitcoin/orderbook",
                json={"markets": ["KRW-BTC"], "level": "10000", "count": 1},
            )
            instruments = client.post(
                "/bitcoin/orderbook/instruments", json={"markets": ["KRW-BTC"]}
            )
            trades = client.post(
                "/bitcoin/trades",
                json={"market": "KRW-BTC", "count": 2, "days_ago": 1},
            )

    assert pairs.status_code == 200
    assert pairs.json() == [
        {
            "market": "KRW-BTC",
            "korean_name": "비트코인",
            "english_name": "Bitcoin",
            "market_warning": None,
            "market_event": {
                "warning": False,
                "caution": {
                    "PRICE_FLUCTUATIONS": False,
                    "TRADING_VOLUME_SOARING": False,
                    "DEPOSIT_AMOUNT_SOARING": False,
                    "GLOBAL_PRICE_DIFFERENCES": False,
                    "CONCENTRATION_OF_SMALL_ACCOUNTS": False,
                },
            },
        }
    ]
    assert ticker.status_code == 200
    assert ticker.json()[0]["trade_price"] == 148601000
    assert quote.status_code == 200
    assert quote.json()[0]["market"] == "KRW-BTC"
    assert orderbook.status_code == 200
    assert orderbook.json()[0]["level"] == 10000
    assert "level" not in orderbook.json()[0]["orderbook_units"][0]
    assert instruments.status_code == 200
    assert instruments.json()[0]["supported_levels"] == ["0", "10000"]
    assert trades.status_code == 200
    assert trades.json()[0]["sequential_id"] == 17510687993360000

    services["trading_pair_service"].get_trading_pairs.assert_called_once_with(True)
    services["ticker_service"].get_tickers.assert_called_once_with(["KRW-BTC"])
    services["quote_ticker_service"].get_tickers.assert_called_once_with(["KRW"])
    services["orderbook_service"].get_orderbooks.assert_called_once_with(
        ["KRW-BTC"], level="10000", count=1
    )
    services[
        "orderbook_instrument_service"
    ].get_orderbook_instruments.assert_called_once_with(["KRW-BTC"])
    services["trade_service"].get_trades.assert_called_once_with(
        market="KRW-BTC", to=None, count=2, cursor=None, days_ago=1
    )


def test_bitcoin_routes_reject_invalid_inputs_before_service_calls():
    with TestClient(main.app) as client:
        empty_markets = client.post("/bitcoin/ticker", json={"markets": []})
        malformed_market = client.post("/bitcoin/ticker", json={"markets": ["krw-btc"]})
        invalid_quote = client.post(
            "/bitcoin/ticker/quote", json={"quote_currencies": ["EUR"]}
        )
        excessive_count = client.post(
            "/bitcoin/orderbook", json={"markets": ["KRW-BTC"], "count": 31}
        )
        zero_count = client.post(
            "/bitcoin/orderbook", json={"markets": ["KRW-BTC"], "count": 0}
        )
        invalid_level = client.post(
            "/bitcoin/orderbook", json={"markets": ["KRW-BTC"], "level": "1.5"}
        )
        decimal_integer_level = client.post(
            "/bitcoin/orderbook", json={"markets": ["KRW-BTC"], "level": "1.0"}
        )
        invalid_trade = client.post(
            "/bitcoin/trades", json={"market": "KRW-BTC", "days_ago": 8}
        )

    assert all(
        response.status_code == 422
        for response in (
            empty_markets,
            malformed_market,
            invalid_quote,
            excessive_count,
            zero_count,
            invalid_level,
            decimal_integer_level,
            invalid_trade,
        )
    )


def test_bitcoin_routes_map_upbit_app_errors_to_their_http_status():
    from stock.domain.exceptions import ExternalApiError, NotFoundError

    pair_service = Mock()
    pair_service.get_trading_pairs.side_effect = NotFoundError(
        "not found", diagnostic="Upbit GET failed path=/v1/market/all status=404"
    )
    ticker_service = Mock()
    ticker_service.get_tickers.side_effect = ExternalApiError(
        "upstream failed", diagnostic="Upbit GET failed path=/v1/ticker status=429"
    )

    with main.container.trading_pair_service.override(providers.Object(pair_service)):
        with main.container.ticker_service.override(providers.Object(ticker_service)):
            with TestClient(main.app) as client:
                not_found = client.post("/bitcoin/trading-pairs", json={})
                upstream_error = client.post(
                    "/bitcoin/ticker", json={"markets": ["KRW-BTC"]}
                )

    assert not_found.status_code == 404
    assert upstream_error.status_code == 502


def make_candle():
    return Candle(
        market="KRW-BTC",
        candle_date_time_utc="2025-06-30T23:59:59",
        candle_date_time_kst="2025-07-01T08:59:59",
        opening_price=145794000,
        high_price=145794000,
        low_price=145759000,
        trade_price=145759000,
        timestamp=1751327999833,
        candle_acc_trade_price=185042,
        candle_acc_trade_volume=0.0013,
    )


def test_bitcoin_candle_routes_convert_all_six_shapes_and_forward_parameters():
    service = Mock()
    service.get_seconds_candles.return_value = [make_candle()]
    service.get_minute_candles.return_value = [
        MinuteCandle(**vars(make_candle()), unit=5)
    ]
    service.get_day_candles.return_value = [
        DayCandle(
            **vars(make_candle()),
            prev_closing_price=147996000,
            change_price=-2237000,
            change_rate=-0.0151152734,
            converted_trade_price=145759000,
        )
    ]
    period_candle = PeriodCandle(
        **vars(make_candle()), first_day_of_period="2025-06-30"
    )
    service.get_week_candles.return_value = [period_candle]
    service.get_month_candles.return_value = [period_candle]
    service.get_year_candles.return_value = [period_candle]

    with main.container.candle_service.override(providers.Object(service)):
        with TestClient(main.app) as client:
            seconds = client.post(
                "/bitcoin/candles/seconds",
                json={"market": "KRW-BTC", "count": 2},
            )
            minutes = client.post(
                "/bitcoin/candles/minutes/5",
                json={
                    "market": "KRW-BTC",
                    "to": "2025-07-01T00:00:00Z",
                    "count": 3,
                },
            )
            days = client.post(
                "/bitcoin/candles/days",
                json={
                    "market": "KRW-BTC",
                    "count": 4,
                    "converting_price_unit": "KRW",
                },
            )
            weeks = client.post("/bitcoin/candles/weeks", json={"market": "KRW-BTC"})
            months = client.post("/bitcoin/candles/months", json={"market": "KRW-BTC"})
            years = client.post("/bitcoin/candles/years", json={"market": "KRW-BTC"})

    assert seconds.status_code == minutes.status_code == days.status_code == 200
    assert weeks.status_code == months.status_code == years.status_code == 200
    assert seconds.json()[0]["candle_date_time_utc"] == "2025-06-30T23:59:59"
    assert minutes.json()[0]["unit"] == 5
    assert days.json()[0]["prev_closing_price"] == 147996000
    assert days.json()[0]["converted_trade_price"] == 145759000
    assert weeks.json()[0]["first_day_of_period"] == "2025-06-30"
    assert months.json()[0]["first_day_of_period"] == "2025-06-30"
    assert years.json()[0]["first_day_of_period"] == "2025-06-30"
    service.get_seconds_candles.assert_called_once_with(
        market="KRW-BTC", to=None, count=2
    )
    service.get_minute_candles.assert_called_once_with(
        5, market="KRW-BTC", to="2025-07-01T00:00:00Z", count=3
    )
    service.get_day_candles.assert_called_once_with(
        market="KRW-BTC", to=None, count=4, converting_price_unit="KRW"
    )
    service.get_week_candles.assert_called_once_with(market="KRW-BTC", to=None, count=1)
    service.get_month_candles.assert_called_once_with(
        market="KRW-BTC", to=None, count=1
    )
    service.get_year_candles.assert_called_once_with(market="KRW-BTC", to=None, count=1)


def test_bitcoin_candle_routes_reject_invalid_input_with_422():
    service = Mock()
    with main.container.candle_service.override(providers.Object(service)):
        with TestClient(main.app) as client:
            missing_market = client.post("/bitcoin/candles/seconds", json={})
            malformed_market = client.post(
                "/bitcoin/candles/seconds", json={"market": "krw-btc"}
            )
            zero_count = client.post(
                "/bitcoin/candles/seconds",
                json={"market": "KRW-BTC", "count": 0},
            )
            excessive_count = client.post(
                "/bitcoin/candles/seconds",
                json={"market": "KRW-BTC", "count": 201},
            )
            invalid_to = client.post(
                "/bitcoin/candles/seconds",
                json={"market": "KRW-BTC", "to": "2025-02-30T00:00:00"},
            )
            invalid_unit = client.post(
                "/bitcoin/candles/minutes/2", json={"market": "KRW-BTC"}
            )
            invalid_converting_unit = client.post(
                "/bitcoin/candles/days",
                json={"market": "KRW-BTC", "converting_price_unit": "BTC"},
            )

    assert all(
        response.status_code == 422
        for response in (
            missing_market,
            malformed_market,
            zero_count,
            excessive_count,
            invalid_to,
            invalid_unit,
            invalid_converting_unit,
        )
    )
    service.get_seconds_candles.assert_not_called()
    service.get_minute_candles.assert_not_called()
    service.get_day_candles.assert_not_called()
