"""KIS API 응답 숫자 정규화와 일봉 조회 구간 분할 유틸리티."""

from common.exchange_calendar import get_krx_calendar

MAX_CALLABLE_DATES = 100
# 조회 지표와 KIS 시계열은 거래일 단위로 맞춰 항상 일봉을 요청한다.
DAILY_PERIOD_CODE = "D"


def to_float(value: str | int | float | None) -> float:
    """KIS 응답의 빈 문자열 숫자 필드를 float 기본값으로 정규화한다."""

    if value in (None, ""):
        return 0.0
    return float(value)


def to_int(value: str | int | float | None) -> int:
    """KIS 응답의 빈 문자열 숫자 필드를 int 기본값으로 정규화한다."""

    if value in (None, ""):
        return 0
    return int(float(value))


def split_date_range(start_date: str, end_date: str) -> list[tuple[str, str]]:
    """KIS 차트 요청의 100건 한도에 맞춰 날짜 범위를 거래일 100개씩 나눈다."""

    sessions = get_krx_calendar().sessions_in_range(start_date, end_date)
    session_dates = [session.strftime("%Y%m%d") for session in sessions]
    chunks = [
        session_dates[index : index + MAX_CALLABLE_DATES]
        for index in range(0, len(session_dates), MAX_CALLABLE_DATES)
    ]

    return [(chunk[0], chunk[-1]) for chunk in chunks]
