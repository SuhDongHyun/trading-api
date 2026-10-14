from datetime import datetime
from unittest.mock import Mock

from dependency_injector import providers
from fastapi.testclient import TestClient

import main
from stock.domain.account import Account, AccountSummary, Position
from stock.domain.indicator import MacdSignal, MovingAverage
from stock.domain.market import OverseasMarketIndexPrice
from stock.domain.news import News
from stock.service.market_index_service import MarketIndexService


def test_treasury_yield_route_uses_enum_mapping_and_attribute_response():
    domestic = Mock()
    overseas = Mock()
    overseas.get_overseas_market_index_prices.return_value = [
        OverseasMarketIndexPrice(
            date="20260401",
            open_price=3.1,
            high_price=3.2,
            low_price=3.0,
            close_price=3.15,
        )
    ]
    service = MarketIndexService(domestic, overseas, Mock(), Mock(), Mock(), Mock())

    with main.container.market_index_service.override(providers.Object(service)):
        with TestClient(main.app) as client:
            response = client.post(
                "/market-index/treasury-yield/korea-3y",
                json={"start_date": "20260401", "end_date": "20260407"},
            )
            invalid_maturity = client.post(
                "/market-index/treasury-yield/korea-2y",
                json={"start_date": "20260401", "end_date": "20260407"},
            )

    assert response.status_code == 200
    assert response.json() == [{"date": "20260401", "yield_rate": 3.15}]
    overseas.get_overseas_market_index_prices.assert_called_once_with(
        "I", "Y0101", "20260401", "20260407"
    )
    assert invalid_maturity.status_code == 422


def test_account_route_validates_nested_dataclasses_from_attributes():
    account_service = Mock()
    account_service.get_account_info.return_value = AccountSummary(
        positions=[Position("005930", "삼성전자", 2, 100.0, 1.2)],
        accounts=[Account(1000.0, 100.0, 1.2)],
    )

    with main.container.account_service.override(providers.Object(account_service)):
        with TestClient(main.app) as client:
            response = client.get("/account")

    assert response.status_code == 200
    assert response.json() == {
        "positions": [
            {
                "code": "005930",
                "name": "삼성전자",
                "quantity": 2.0,
                "unrealized_pnl": 100.0,
                "unrealized_return": 1.2,
            }
        ],
        "accounts": [{"cash_balance": 1000.0, "total_pnl": 100.0, "total_return": 1.2}],
    }


def test_stock_quote_route_requires_dates_and_forbids_removed_fields():
    with TestClient(main.app) as client:
        missing_dates = client.post("/stock_quote/daily", json={})
        invalid_date = client.post(
            "/stock_quote/daily",
            json={"start_date": "20240230", "end_date": "20240301"},
        )
        removed_period = client.post(
            "/stock_quote/daily",
            json={
                "start_date": "20260401",
                "end_date": "20260407",
                "period": "D",
            },
        )

    assert missing_dates.status_code == 422
    assert invalid_date.status_code == 422
    assert removed_period.status_code == 422


def test_indicator_routes_serialize_aliased_values_with_response_field_names():
    stock_quote_service = Mock()
    stock_quote_service.get_moving_average.return_value = [
        MovingAverage(date="20260401", value=123.45)
    ]
    stock_quote_service.get_macd_signal.return_value = [
        MacdSignal(date="20260401", value=0.25, signal="buy")
    ]

    with main.container.stock_quote_service.override(
        providers.Object(stock_quote_service)
    ):
        with TestClient(main.app) as client:
            moving_average = client.post(
                "/stock_quote/daily/moving-average",
                json={"start_date": "20260401", "end_date": "20260402"},
            )
            macd_signal = client.post(
                "/stock_quote/indicator/macd-signal",
                json={"start_date": "20260401", "end_date": "20260402"},
            )

    assert moving_average.status_code == 200
    assert moving_average.json() == [{"date": "20260401", "moving_average": 123.45}]
    assert macd_signal.status_code == 200
    assert macd_signal.json() == [
        {"date": "20260401", "macd_ema": 0.25, "signal": "buy"}
    ]


def test_news_response_schema_reads_dataclass_attributes():
    news_service = Mock()
    news_service.get_total_news.return_value = [
        News(
            key="1",
            title="시장 동향",
            source="신문",
            published_at=datetime(2026, 4, 1, 9),
        )
    ]

    with main.container.stock_news_service.override(providers.Object(news_service)):
        with TestClient(main.app) as client:
            invalid_date = client.post(
                "/stock_news",
                json={"search_date": "20240230", "search_time": "090000"},
            )
            response = client.post(
                "/stock_news",
                json={"search_date": "20260401", "search_time": "090000"},
            )

    assert invalid_date.status_code == 422
    assert response.status_code == 200
    news_service.get_total_news.assert_called_once_with(
        code="005930", search_date="20260401", search_time="090000"
    )
    assert response.json() == [
        {
            "title": "시장 동향",
            "source": "신문",
            "published_at": "2026-04-01T09:00:00",
        }
    ]
