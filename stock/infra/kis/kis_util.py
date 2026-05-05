"""KIS API 응답에서 숫자 필드의 빈 문자열을 기본값으로 정규화하는 유틸리티 함수와 날짜 범위를 분할하는 함수."""

import exchange_calendars as xcals

MAX_CALLABLE_DATES = 100


def _to_float(value: str | int | float | None) -> float:
    """KIS 응답의 빈 문자열 숫자 필드를 float 기본값으로 정규화한다."""

    if value in (None, ""):
        return 0.0
    return float(value)


def _to_int(value: str | int | float | None) -> int:
    """KIS 응답의 빈 문자열 숫자 필드를 int 기본값으로 정규화한다."""

    if value in (None, ""):
        return 0
    return int(float(value))


def split_date_range(start_date: str, end_date: str) -> list[tuple[str, str]]:
    """주어진 날짜 범위를 MAX_CALLABLE_DATES 크기로 분할한다."""
    cal = xcals.get_calendar("XKRX")  # 한국거래소 KRX
    sessions = cal.sessions_in_range(start_date, end_date)
    split_sessions = [
        sessions[i : i + MAX_CALLABLE_DATES]
        for i in range(0, len(sessions), MAX_CALLABLE_DATES)
    ]

    return [
        (session[0].strftime("%Y%m%d"), session[-1].strftime("%Y%m%d"))
        for session in split_sessions
    ]
