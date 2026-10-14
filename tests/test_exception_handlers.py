import logging

import pytest
import requests
from dependency_injector import providers
from fastapi.testclient import TestClient
from requests import Response

import main
from stock.domain.exceptions import ExternalApiError
from stock.service.stock_quote_service import StockQuoteService


class EmptyQuoteClient:
    def get_daily_stock_prices(self, **kwargs):
        return []


class FailingQuoteClient:
    def __init__(self, error):
        self.error = error

    def get_daily_stock_prices(self, **kwargs):
        raise self.error


def daily_quote_payload():
    return {
        "market": "J",
        "code": "005930",
        "start_date": "20240401",
        "end_date": "20240405",
    }


def test_empty_daily_history_maps_to_not_found_in_main_app(caplog):
    service = StockQuoteService(EmptyQuoteClient())
    with main.container.stock_quote_service.override(providers.Object(service)):
        with caplog.at_level(logging.ERROR):
            response = TestClient(main.app).post(
                "/stock_quote/daily", json=daily_quote_payload()
            )

    assert response.status_code == 404
    assert "005930" in response.json()["detail"]
    assert "NotFoundError" in caplog.text


def test_request_error_logs_safe_upstream_diagnostics_once(caplog):
    prepared_request = requests.Request(
        "GET",
        "https://kis.example/uapi/test?CANO=12345678&ACNT_PRDT_CD=01",
        headers={
            "tr_id": "FHKST01011800",
            "authorization": "Bearer hidden-token",
            "appkey": "hidden-app-key",
        },
    ).prepare()
    upstream_response = Response()
    upstream_response.status_code = 500
    upstream_response.url = prepared_request.url
    upstream_response.request = prepared_request
    upstream_response._content = b'{"msg_cd":"EGW00201","msg1":"KIS request limit"}'
    error = requests.HTTPError(
        "upstream failed", request=prepared_request, response=upstream_response
    )
    service = StockQuoteService(FailingQuoteClient(error))
    with main.container.stock_quote_service.override(providers.Object(service)):
        with caplog.at_level(logging.ERROR):
            response = TestClient(main.app).post(
                "/stock_quote/daily", json=daily_quote_payload()
            )

    assert response.status_code == 502
    assert "path=/uapi/test" in caplog.text
    assert "status=500" in caplog.text
    assert "tr_id=FHKST01011800" in caplog.text
    assert "EGW00201" in caplog.text
    assert "KIS request limit" in caplog.text
    assert "12345678" not in caplog.text
    assert "hidden-token" not in caplog.text
    assert "hidden-app-key" not in caplog.text
    assert caplog.text.count("External HTTP request failed") == 1


@pytest.mark.parametrize("error_type", [requests.Timeout, requests.ConnectionError])
def test_network_errors_map_to_502_without_logging_query(caplog, error_type):
    prepared_request = requests.Request(
        "GET",
        "https://kis.example/uapi/account?CANO=12345678",
        headers={"tr_id": "TTTC8434R"},
    ).prepare()
    error = error_type("upstream unavailable", request=prepared_request)
    service = StockQuoteService(FailingQuoteClient(error))
    with main.container.stock_quote_service.override(providers.Object(service)):
        with caplog.at_level(logging.ERROR):
            response = TestClient(main.app).post(
                "/stock_quote/daily", json=daily_quote_payload()
            )

    assert response.status_code == 502
    assert "path=/uapi/account" in caplog.text
    assert "12345678" not in caplog.text
    assert "External HTTP request failed" in caplog.text


def test_app_error_uses_its_status_code_and_logs_diagnostics(caplog):
    error = ExternalApiError("KIS API 요청에 실패했습니다.", diagnostic="KIS msg_cd=X")
    service = StockQuoteService(FailingQuoteClient(error))
    with main.container.stock_quote_service.override(providers.Object(service)):
        with caplog.at_level(logging.ERROR):
            response = TestClient(main.app).post(
                "/stock_quote/daily", json=daily_quote_payload()
            )

    assert response.status_code == 502
    assert response.json() == {"detail": "KIS API 요청에 실패했습니다."}
    assert "diagnostic=KIS msg_cd=X" in caplog.text
    assert caplog.text.count("Application error") == 1


def test_invalid_ema_window_is_rejected_by_actual_request_schema():
    response = TestClient(main.app).post(
        "/stock_quote/indicator/macd", json={"ema_long_window": 1}
    )

    assert response.status_code == 422
