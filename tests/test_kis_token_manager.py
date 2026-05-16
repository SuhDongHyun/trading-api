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
