import threading
import time

import pytest

from stock.infra.kis import kis_token_manager


@pytest.fixture(autouse=True)
def clear_token_cache():
    kis_token_manager.clear_access_token_cache()
    yield
    kis_token_manager.clear_access_token_cache()


def test_access_token_is_issued_once_under_concurrent_first_access(monkeypatch):
    """동시 최초 접근에서도 KIS 토큰 발급은 한 번만 수행한다."""

    issued_tokens = []

    def fake_issue_access_token():
        time.sleep(0.05)
        token = f"token-{len(issued_tokens) + 1}"
        issued_tokens.append(token)
        return token, time.time() + 86400

    monkeypatch.setattr(kis_token_manager, "_issue_access_token", fake_issue_access_token)

    results = []
    threads = [
        threading.Thread(target=lambda: results.append(kis_token_manager.get_access_token()))
        for _ in range(5)
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert issued_tokens == ["token-1"]
    assert results == ["token-1"] * 5


def test_issue_access_token_uses_expires_in_with_safety_buffer(monkeypatch):
    """서버 시간대와 무관하게 expires_in에서 안전 여유를 뺀 시각을 사용한다."""

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "access_token": "issued-token",
                "access_token_token_expired": "2026-06-24 22:03:52",
                "token_type": "Bearer",
                "expires_in": 86400,
            }

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(kis_token_manager.requests, "post", fake_post)
    monkeypatch.setattr(kis_token_manager.time, "time", lambda: 1000.0)

    token, exp_epoch = kis_token_manager._issue_access_token()

    assert token == "issued-token"
    assert kis_token_manager.TOKEN_EXPIRY_BUFFER_SECONDS == 60
    assert (
        exp_epoch
        == 1000.0 + 86400 - kis_token_manager.TOKEN_EXPIRY_BUFFER_SECONDS
    )
