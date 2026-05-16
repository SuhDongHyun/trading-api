import asyncio
import threading
import time

import pytest

import common.exchange_calendar as exchange_calendar
import main


@pytest.fixture(autouse=True)
def clear_calendar_cache():
    exchange_calendar.clear_exchange_calendar_cache()
    yield
    exchange_calendar.clear_exchange_calendar_cache()


def test_exchange_calendar_is_created_once_under_concurrent_first_access(monkeypatch):
    """동시 최초 접근에서도 거래소 캘린더 생성은 한 번만 수행한다."""

    created_calendars = []

    def fake_get_calendar(name):
        time.sleep(0.05)
        calendar = object()
        created_calendars.append((name, calendar))
        return calendar

    exchange_calendar.clear_exchange_calendar_cache()
    monkeypatch.setattr(exchange_calendar.xcals, "get_calendar", fake_get_calendar)

    results = []
    threads = [
        threading.Thread(
            target=lambda: results.append(exchange_calendar.get_exchange_calendar("XKRX"))
        )
        for _ in range(5)
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(created_calendars) == 1
    assert len(results) == 5
    assert all(result is created_calendars[0][1] for result in results)


def test_startup_warms_up_krx_calendar(monkeypatch):
    """앱 시작 시 KRX 캘린더를 미리 생성한다."""

    calls = []

    monkeypatch.setattr(main, "get_krx_calendar", lambda: calls.append("XKRX"))

    async def run_lifespan():
        async with main.lifespan(main.app):
            pass

    asyncio.run(run_lifespan())

    assert calls == ["XKRX"]
