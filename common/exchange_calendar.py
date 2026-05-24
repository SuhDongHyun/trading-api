"""거래소 캘린더 객체를 공통으로 재사용하는 helper."""

from threading import Lock

import exchange_calendars as xcals

DEFAULT_START_DATE = "19850130"

_calendar_lock = Lock()
_calendars = {}


def get_exchange_calendar(name: str):
    """거래소 캘린더 객체를 프로세스 안에서 재사용한다."""

    with _calendar_lock:
        calendar = _calendars.get(name)
        if calendar is None:
            calendar = xcals.get_calendar(name, start=DEFAULT_START_DATE)
            _calendars[name] = calendar
        return calendar


def clear_exchange_calendar_cache():
    """프로세스 안의 거래소 캘린더 캐시를 초기화한다."""

    with _calendar_lock:
        _calendars.clear()


def get_krx_calendar():
    """한국거래소 XKRX 캘린더를 반환한다."""

    return get_exchange_calendar("XKRX")
