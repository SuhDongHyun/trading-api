"""KIS API 응답 정규화와 일봉 차트 구간 조회 유틸리티."""

from datetime import datetime, timedelta
from typing import Any, Callable

from common.exchange_calendar import get_krx_calendar

MAX_CALLABLE_DATES = 100
# 조회 지표와 KIS 시계열은 거래일 단위로 맞춰 항상 일봉을 요청한다.
DAILY_PERIOD_CODE = "D"


def to_float(value: str | int | float | None) -> float:
    """KIS 응답의 빈 문자열 숫자 필드를 float 기본값으로 정규화한다."""

    if value in (None, ""):
        return 0.0
    return float(value)


def to_optional_float(value: str | int | float | None) -> float | None:
    """KIS 응답에서 값이 빠진 선택 숫자 필드를 None으로 보존한다."""

    if value in (None, ""):
        return None
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


def split_calendar_date_range(start_date: str, end_date: str) -> list[tuple[str, str]]:
    """해외 일봉은 KRX 휴장일에 빠지지 않도록 최대 100달력일씩 자른다."""

    start = datetime.strptime(start_date, "%Y%m%d").date()
    end = datetime.strptime(end_date, "%Y%m%d").date()
    chunks = []
    chunk_start = start

    while chunk_start <= end:
        chunk_end = min(chunk_start + timedelta(days=MAX_CALLABLE_DATES - 1), end)
        chunks.append((chunk_start.strftime("%Y%m%d"), chunk_end.strftime("%Y%m%d")))
        chunk_start = chunk_end + timedelta(days=1)

    return chunks


def fetch_daily_chart_prices(
    start_date: str,
    end_date: str,
    fetch_page: Callable[[str, str], dict[str, Any]],
    *,
    split_range: Callable[[str, str], list[tuple[str, str]]] = split_date_range,
) -> list[dict[str, Any]]:
    """100건 상한으로 나눈 KIS 페이지를 시간순으로 합친다.

    국내 API 구간은 KRX 거래일로 잘라 정확히 100세션씩 조회한다. 해외 API는
    KRX 달력과 휴장일이 다르므로 100달력일 이하로 제한해 응답 누락을 막는다.
    KIS 페이지 내부는 최신순이라 각 페이지를 뒤집은 뒤 구간 순서대로 합친다.
    """

    return [
        item
        for chunk_start, chunk_end in split_range(start_date, end_date)
        for item in fetch_page(chunk_start, chunk_end)["output2"][::-1]
    ]
