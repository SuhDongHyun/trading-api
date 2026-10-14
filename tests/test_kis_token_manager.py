import threading
import time
from unittest.mock import Mock

import pytest

from config import KISSetting
from stock.domain.exceptions import ExternalApiError
from stock.infra.kis.kis_token_manager import (
    TOKEN_EXPIRY_BUFFER_SECONDS,
    KisTokenManager,
)


def make_settings():
    return KISSetting(
        base_url="https://example.test",
        account_num="12345678",
        account_code="01",
        appkey="test-key",
        appsecret="test-secret",
    )


def test_access_token_is_issued_once_under_concurrent_first_access(monkeypatch):
    """동시 최초 접근에서도 하나의 토큰만 발급한다."""

    manager = KisTokenManager(make_settings())
    issued_tokens = []

    def fake_issue_access_token():
        time.sleep(0.05)
        token = f"token-{len(issued_tokens) + 1}"
        issued_tokens.append(token)
        return token, time.time() + 86400

    monkeypatch.setattr(manager, "_issue_access_token", fake_issue_access_token)
    results = []
    threads = [
        threading.Thread(target=lambda: results.append(manager.get_access_token()))
        for _ in range(5)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert issued_tokens == ["token-1"]
    assert results == ["token-1"] * 5


def test_issue_access_token_uses_expires_in_with_safety_buffer():
    """expires_in에서 안전 여유를 빼 만료 직전의 토큰 사용을 피한다."""

    response = Mock()
    response.json.return_value = {
        "access_token": "issued-token",
        "access_token_token_expired": "2026-06-24 22:03:52",
        "token_type": "Bearer",
        "expires_in": 86400,
    }
    response.raise_for_status.return_value = None
    post = Mock(return_value=response)
    manager = KisTokenManager(make_settings(), post=post, clock=lambda: 1000.0)

    token, exp_epoch = manager._issue_access_token()

    assert token == "issued-token"
    assert TOKEN_EXPIRY_BUFFER_SECONDS == 60
    assert exp_epoch == 1000.0 + 86400 - TOKEN_EXPIRY_BUFFER_SECONDS
    post.assert_called_once_with(
        "https://example.test/oauth2/tokenP",
        headers={"content-type": "application/json"},
        json={
            "grant_type": "client_credentials",
            "appkey": "test-key",
            "appsecret": "test-secret",
        },
        timeout=10,
    )


def test_issue_access_token_error_diagnostic_keeps_kis_error_fields():
    response = Mock()
    response.json.return_value = {
        "error_code": "EGW00133",
        "error_description": "token issue limit",
    }
    response.raise_for_status.return_value = None
    manager = KisTokenManager(
        make_settings(), post=Mock(return_value=response), clock=lambda: 1000.0
    )

    with pytest.raises(ExternalApiError) as error:
        manager._issue_access_token()

    assert error.value.status_code == 502
    assert "EGW00133" in error.value.diagnostic
    assert "token issue limit" in error.value.diagnostic
