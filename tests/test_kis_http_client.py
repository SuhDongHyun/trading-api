import logging

import pytest
from requests import ConnectionError, HTTPError, Response

from stock.infra.kis import kis_http_client


def make_response(status_code: int, url: str, body: str) -> Response:
    response = Response()
    response.status_code = status_code
    response.url = url
    response._content = body.encode()
    return response


def test_api_get_logs_kis_error_response_without_sensitive_headers(
    monkeypatch, caplog
):
    response = make_response(
        500,
        "https://openapi.koreainvestment.com:9443/uapi/test",
        '{"msg_cd":"EGW00123","msg1":"KIS failure"}',
    )

    monkeypatch.setattr(kis_http_client, "acquire_kis_api_slot", lambda: None)
    monkeypatch.setattr(
        kis_http_client,
        "build_header",
        lambda tr_id, extra_headers: {
            "authorization": "Bearer token",
            "appkey": "secret-key",
            "appsecret": "secret-value",
            "tr_id": tr_id,
        },
    )
    monkeypatch.setattr(kis_http_client, "get", lambda **kwargs: response)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(HTTPError):
            kis_http_client.api_get(
                path="/uapi/test",
                params={"FID_INPUT_ISCD": "000660"},
                tr_id="FHKST01011800",
            )

    assert "KIS GET failed" in caplog.text
    assert "status=500" in caplog.text
    assert "FHKST01011800" in caplog.text
    assert "KIS failure" in caplog.text
    assert "Bearer token" not in caplog.text
    assert "secret-key" not in caplog.text
    assert "secret-value" not in caplog.text


def test_api_post_logs_kis_error_response_without_sensitive_headers(
    monkeypatch, caplog
):
    response = make_response(
        500,
        "https://openapi.koreainvestment.com:9443/uapi/test",
        '{"msg_cd":"EGW00123","msg1":"KIS failure"}',
    )

    monkeypatch.setattr(kis_http_client, "acquire_kis_api_slot", lambda: None)
    monkeypatch.setattr(
        kis_http_client,
        "build_header",
        lambda tr_id, extra_headers: {
            "authorization": "Bearer token",
            "appkey": "secret-key",
            "appsecret": "secret-value",
            "tr_id": tr_id,
        },
    )
    monkeypatch.setattr(kis_http_client, "post", lambda **kwargs: response)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(HTTPError):
            kis_http_client.api_post(
                path="/uapi/test",
                body={"FID_INPUT_ISCD": "000660"},
                tr_id="FHKST01011800",
            )

    assert "KIS POST failed" in caplog.text
    assert "status=500" in caplog.text
    assert "FHKST01011800" in caplog.text
    assert "KIS failure" in caplog.text
    assert "Bearer token" not in caplog.text
    assert "secret-key" not in caplog.text
    assert "secret-value" not in caplog.text


def test_api_get_uses_timeout_and_logs_connection_errors_without_sensitive_headers(
    monkeypatch, caplog
):
    def raise_connection_error(**kwargs):
        raise ConnectionError("remote disconnected")

    monkeypatch.setattr(kis_http_client, "acquire_kis_api_slot", lambda: None)
    monkeypatch.setattr(
        kis_http_client,
        "build_header",
        lambda tr_id, extra_headers: {
            "authorization": "Bearer token",
            "appkey": "secret-key",
            "appsecret": "secret-value",
            "tr_id": tr_id,
        },
    )
    monkeypatch.setattr(kis_http_client, "get", raise_connection_error)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(ConnectionError):
            kis_http_client.api_get(
                path="/uapi/test",
                params={"FID_INPUT_ISCD": "000660"},
                tr_id="FHKST01011800",
            )

    assert "KIS GET connection failed" in caplog.text
    assert "FHKST01011800" in caplog.text
    assert "FID_INPUT_ISCD" in caplog.text
    assert "Bearer token" not in caplog.text
    assert "secret-key" not in caplog.text
    assert "secret-value" not in caplog.text


def test_api_post_uses_timeout(monkeypatch):
    captured_kwargs = {}
    response = make_response(
        200,
        "https://openapi.koreainvestment.com:9443/uapi/test",
        '{"rt_cd":"0"}',
    )

    def capture_post(**kwargs):
        captured_kwargs.update(kwargs)
        return response

    monkeypatch.setattr(kis_http_client, "acquire_kis_api_slot", lambda: None)
    monkeypatch.setattr(
        kis_http_client,
        "build_header",
        lambda tr_id, extra_headers: {"tr_id": tr_id},
    )
    monkeypatch.setattr(kis_http_client, "post", capture_post)

    kis_http_client.api_post(
        path="/uapi/test",
        body={"code": "005930"},
        tr_id="TEST",
    )

    assert captured_kwargs["timeout"] == kis_http_client.KIS_REQUEST_TIMEOUT_SECONDS
