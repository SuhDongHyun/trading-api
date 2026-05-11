"""거래소 캘린더 객체를 공통으로 재사용하는 helper."""

from functools import lru_cache

import exchange_calendars as xcals


@lru_cache(maxsize=None)
def get_exchange_calendar(name: str):
    """거래소 캘린더 객체를 프로세스 안에서 재사용한다."""

    return xcals.get_calendar(name)


def get_krx_calendar():
    """한국거래소 XKRX 캘린더를 반환한다."""

    return get_exchange_calendar("XKRX")
