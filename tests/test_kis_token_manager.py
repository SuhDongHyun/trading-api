import threading
import time
from datetime import datetime

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


def test_issue_access_token_uses_api_expired_at(monkeypatch):
    """KIS 응답의 명시적인 토큰 만료 시각을 캐시 만료 시각으로 사용한다."""

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

    token, exp_epoch = kis_token_manager._issue_access_token()

    assert token == "issued-token"
    assert exp_epoch == datetime.strptime(
        "2026-06-24 22:03:52", "%Y-%m-%d %H:%M:%S"
    ).timestamp()
