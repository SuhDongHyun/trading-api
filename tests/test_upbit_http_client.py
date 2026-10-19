from unittest.mock import Mock

import pytest

from bitcoin.infra.upbit.upbit_http_client import UpbitHttpClient
from config import UpbitSetting
from stock.domain.exceptions import ExternalApiError, NotFoundError


class FakeResponse:
    def __init__(self, status_code: int, body: dict | list | None = None):
        self.status_code = status_code
        self._body = body

    def json(self):
        if self._body is None:
            raise ValueError("no JSON")
        return self._body


def make_client(response: FakeResponse):
    get = Mock(return_value=response)
    limiter = Mock()
    client = UpbitHttpClient(
        upbit_settings=UpbitSetting(base_url="https://api.upbit.com"),
        rate_limiter=limiter,
        get=get,
    )
    return client, get, limiter


def test_upbit_http_client_sends_public_get_with_timeout_and_rate_group():
    client, get, limiter = make_client(FakeResponse(200, []))

    response = client.get(
        "/v1/ticker", params={"markets": "KRW-BTC"}, rate_limit_group="ticker"
    )

    assert response.status_code == 200
    limiter.acquire.assert_called_once_with("ticker")
    get.assert_called_once_with(
        url="https://api.upbit.com/v1/ticker",
        params={"markets": "KRW-BTC"},
        timeout=10,
    )
    assert "headers" not in get.call_args.kwargs


@pytest.mark.parametrize("status_code", [400, 418, 429, 500])
def test_upbit_http_client_maps_non_404_errors_to_external_api_error(status_code):
    client, _, _ = make_client(
        FakeResponse(
            status_code,
            {"error": {"name": "invalid_query_payload", "message": "invalid market"}},
        )
    )

    with pytest.raises(ExternalApiError) as error:
        client.get("/v1/ticker", params={"markets": "KRW-BTC"})

    assert error.value.status_code == 502
    assert "invalid_query_payload" in error.value.diagnostic
    assert "invalid market" in error.value.diagnostic
    assert "?" not in error.value.diagnostic


def test_upbit_http_client_maps_404_and_does_not_log_query_values():
    client, _, _ = make_client(
        FakeResponse(404, {"error": {"name": "market_not_found", "message": "missing"}})
    )

    with pytest.raises(NotFoundError) as error:
        client.get("/v1/ticker", params={"markets": "PRIVATE-VALUE"})

    assert error.value.status_code == 404
    assert "market_not_found" in error.value.diagnostic
    assert "PRIVATE-VALUE" not in error.value.diagnostic
