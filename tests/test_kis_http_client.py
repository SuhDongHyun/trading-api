from unittest.mock import Mock, call

import pytest
from requests import ConnectionError, HTTPError, Response

from config import KISSetting
from stock.domain.exceptions import ExternalApiError
from stock.infra.kis.kis_http_client import (
    KIS_REQUEST_TIMEOUT_SECONDS,
    KisHttpClient,
)


def make_response(status_code: int, url: str, body: str) -> Response:
    response = Response()
    response.status_code = status_code
    response.url = url
    response._content = body.encode()
    return response


def make_client(get=None, headers=None, responses=None):
    token_manager = Mock()
    token_manager.auth_headers.side_effect = headers or [
        {"authorization": "Bearer token", "tr_id": "TEST"}
    ]
    rate_limiter = Mock()
    http_client = KisHttpClient(
        kis_settings=KISSetting(
            base_url="https://openapi.koreainvestment.com:9443",
            account_num="12345678",
            account_code="01",
            appkey="test-key",
            appsecret="test-secret",
        ),
        token_manager=token_manager,
        rate_limiter=rate_limiter,
        get=get or Mock(side_effect=responses),
    )
    return http_client, token_manager, rate_limiter


def test_http_get_raises_http_error_for_global_diagnostics_handler():
    response = make_response(
        500,
        "https://openapi.koreainvestment.com:9443/uapi/test",
        '{"msg_cd":"KIS00000","msg1":"KIS failure"}',
    )
    transport = Mock(return_value=response)
    http_client, _, _ = make_client(
        get=transport,
        headers=[
            {
                "authorization": "Bearer token",
                "appkey": "secret-key",
                "appsecret": "secret-value",
                "tr_id": "FHKST01011800",
            }
        ],
    )

    with pytest.raises(HTTPError):
        http_client.get(
            path="/uapi/test",
            params={"FID_INPUT_ISCD": "000660"},
            tr_id="FHKST01011800",
        )


def test_http_get_refreshes_token_once_when_kis_reports_expired_token():
    responses = [
        make_response(
            500,
            "https://openapi.koreainvestment.com:9443/uapi/test",
            '{"rt_cd":"1","msg_cd":"EGW00123","msg1":"expired"}',
        ),
        make_response(
            200,
            "https://openapi.koreainvestment.com:9443/uapi/test",
            '{"rt_cd":"0","output":[]}',
        ),
    ]
    sent_authorizations = []
    transport = Mock(
        side_effect=lambda **kwargs: (
            sent_authorizations.append(kwargs["headers"]["authorization"])
            or responses.pop(0)
        )
    )
    headers = [
        {"authorization": "Bearer expired-token", "tr_id": "FHKST03030100"},
        {"authorization": "Bearer new-token", "tr_id": "FHKST03030100"},
    ]
    http_client, token_manager, _ = make_client(get=transport, headers=headers)

    response = http_client.get(
        path="/uapi/test", params={"FID_INPUT_ISCD": "FX@KRW"}, tr_id="FHKST03030100"
    )

    assert response.status_code == 200
    assert token_manager.auth_headers.call_args_list == [
        call({"tr_id": "FHKST03030100"}),
        call({"tr_id": "FHKST03030100"}, force_refresh=True),
    ]
    assert sent_authorizations == ["Bearer expired-token", "Bearer new-token"]


def test_http_get_raises_external_api_error_for_kis_business_error():
    response = make_response(
        200,
        "https://openapi.koreainvestment.com:9443/uapi/test",
        '{"rt_cd":"1","msg_cd":"EGW00201","msg1":"request limit"}',
    )
    http_client, _, _ = make_client(get=Mock(return_value=response))

    with pytest.raises(ExternalApiError) as error:
        http_client.get(path="/uapi/test", tr_id="FHKST01011800")

    assert error.value.status_code == 502
    assert "EGW00201" in error.value.diagnostic
    assert "request limit" in error.value.diagnostic


def test_http_get_passes_response_without_rt_cd():
    response = make_response(
        200,
        "https://openapi.koreainvestment.com:9443/uapi/test",
        '{"access_token":"issued-token","expires_in":86400}',
    )
    http_client, _, _ = make_client(get=Mock(return_value=response))

    assert http_client.get(path="/uapi/test") is response


def test_http_get_uses_timeout_and_propagates_connection_errors():
    transport = Mock(side_effect=ConnectionError("remote disconnected"))
    http_client, _, _ = make_client(
        get=transport,
        headers=[
            {
                "authorization": "Bearer token",
                "appkey": "secret-key",
                "appsecret": "secret-value",
                "tr_id": "FHKST01011800",
            }
        ],
    )

    with pytest.raises(ConnectionError):
        http_client.get(
            path="/uapi/test",
            params={"FID_INPUT_ISCD": "000660"},
            tr_id="FHKST01011800",
        )

    assert transport.call_args.kwargs["timeout"] == KIS_REQUEST_TIMEOUT_SECONDS
