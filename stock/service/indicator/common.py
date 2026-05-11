"""여러 기술적 지표 계산에서 공유하는 보조 함수."""

import pandas as pd
from datetime import datetime, timedelta

from common.exchange_calendar import get_krx_calendar

PERIOD_START_NORMALIZERS = {
    "D": lambda date: (
        get_krx_calendar()
        .date_to_session(
            date,
            direction="next",
        )
        .date()
    ),
    "W": lambda date: date - timedelta(days=date.weekday()),
    "M": lambda date: date.replace(day=1),
    "Y": lambda date: date.replace(month=1, day=1),
}


PERIOD_END_NORMALIZERS = {
    "D": lambda date: (
        get_krx_calendar()
        .date_to_session(
            date,
            direction="previous",
        )
        .date()
    ),
    "W": PERIOD_START_NORMALIZERS["W"],
    "M": PERIOD_START_NORMALIZERS["M"],
    "Y": PERIOD_START_NORMALIZERS["Y"],
}

PERIOD_FETCH_START_CALCULATORS = {
    "D": lambda start_date, window: (
        get_krx_calendar().session_offset(start_date, -(window - 1)).date()
    ),
    "W": lambda start_date, window: start_date - timedelta(weeks=window - 1),
    "M": lambda start_date, window: _shift_months(start_date, -(window - 1)),
    "Y": lambda start_date, window: start_date.replace(
        year=start_date.year - (window - 1)
    ),
}


def _to_date(value: str):
    """YYYYMMDD 문자열을 date 객체로 변환한다."""

    return datetime.strptime(value, "%Y%m%d").date()


def _format_date(value) -> str:
    """date 또는 pandas Timestamp 값을 YYYYMMDD 문자열로 변환한다."""

    return value.strftime("%Y%m%d")


def _shift_months(date, months: int):
    """기준 날짜에 지정한 개월 수를 더하거나 빼서 date 객체로 반환한다."""
    return (pd.Timestamp(date) + pd.DateOffset(months=months)).date()


def normalize_period_start(date, period):
    """기간의 시작 날짜를 정규화한다."""

    normalizer = PERIOD_START_NORMALIZERS.get(period)

    if normalizer is None:
        raise ValueError(f"지원하지 않는 기간: {period}")

    return _format_date(normalizer(_to_date(date)))


def normalize_period_end(date, period):
    """기간의 마지막 날짜를 정규화한다."""

    normalizer = PERIOD_END_NORMALIZERS.get(period)

    if normalizer is None:
        raise ValueError(f"지원하지 않는 기간: {period}")

    return _format_date(normalizer(_to_date(date)))


def calculate_indicator_fetch_start_date(start_date, period, window):
    """기간과 창 크기에 따라 데이터를 가져오기 시작할 날짜를 계산한다."""

    calculator = PERIOD_FETCH_START_CALCULATORS.get(period)

    if calculator is None:
        raise ValueError(f"지원하지 않는 기간: {period}")

    return _format_date(calculator(_to_date(start_date), window))


def resolve_indicator_date_range(
    start_date: str, end_date: str, period: str, window: int, extra_periods: int = 0
) -> tuple[str, str]:
    """지표 계산에 필요한 날짜 범위를 정규화하고 계산한다."""

    valid_start_date = normalize_period_start(start_date, period)
    valid_end_date = normalize_period_end(end_date, period)
    fetch_start_date = calculate_indicator_fetch_start_date(
        start_date=valid_start_date,
        period=period,
        window=window + extra_periods,
    )

    return fetch_start_date, valid_end_date
