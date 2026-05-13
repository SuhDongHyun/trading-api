"""지표 계산에 필요한 기간별 KRX 거래일 보정 helper."""

import pandas as pd
from datetime import datetime, timedelta

from common.exchange_calendar import get_krx_calendar


def _to_date(value: str):
    """YYYYMMDD 문자열을 date 객체로 변환한다."""

    return datetime.strptime(value, "%Y%m%d").date()


def _format_date(value) -> str:
    """date 또는 pandas Timestamp 값을 YYYYMMDD 문자열로 변환한다."""

    return value.strftime("%Y%m%d")


def _shift_months(date, months: int):
    """기준 날짜에 지정한 개월 수를 더하거나 빼서 date 객체로 반환한다."""

    return (pd.Timestamp(date) + pd.DateOffset(months=months)).date()


def _first_session_on_or_after(date):
    """기준일 당일 또는 이후의 첫 KRX 거래일을 반환한다."""

    return get_krx_calendar().date_to_session(date, direction="next").date()


def _last_session_on_or_before(date):
    """기준일 당일 또는 이전의 마지막 KRX 거래일을 반환한다."""

    return get_krx_calendar().date_to_session(date, direction="previous").date()


def _week_start(date):
    """기준일이 속한 주의 월요일을 반환한다."""

    return date - timedelta(days=date.weekday())


def _month_start(date):
    """기준일이 속한 월의 1일을 반환한다."""

    return date.replace(day=1)


def _year_start(date):
    """기준일이 속한 연도의 1월 1일을 반환한다."""

    return date.replace(month=1, day=1)


PERIOD_CALENDAR_START_CALCULATORS = {
    "D": lambda date: date,
    "W": _week_start,
    "M": _month_start,
    "Y": _year_start,
}


def _period_calendar_start(date, period):
    """기간 기준 달력상 시작일을 반환한다."""

    calculator = PERIOD_CALENDAR_START_CALCULATORS.get(period)

    if calculator is None:
        raise ValueError(f"지원하지 않는 기간: {period}")

    return calculator(date)


def _first_period_session(date, period):
    """기준일이 속한 기간의 첫 KRX 거래일을 반환한다."""

    return _first_session_on_or_after(_period_calendar_start(date, period))


def _daily_fetch_start_date(start_date, window):
    """일봉 window에 필요한 첫 거래일을 반환한다."""

    return get_krx_calendar().session_offset(start_date, -(window - 1)).date()


def _weekly_fetch_start_date(start_date, window):
    """주봉 window에 필요한 첫 주의 첫 거래일을 반환한다."""

    target_date = _week_start(start_date) - timedelta(weeks=window - 1)
    return _first_period_session(target_date, "W")


def _monthly_fetch_start_date(start_date, window):
    """월봉 window에 필요한 첫 월의 첫 거래일을 반환한다."""

    target_date = _shift_months(_month_start(start_date), -(window - 1))
    return _first_period_session(target_date, "M")


def _yearly_fetch_start_date(start_date, window):
    """년봉 window에 필요한 첫 연도의 첫 거래일을 반환한다."""

    target_year = start_date.year - (window - 1)
    target_date = _year_start(start_date).replace(year=target_year)
    return _first_period_session(target_date, "Y")


PERIOD_START_NORMALIZERS = {
    "D": _first_session_on_or_after,
    "W": lambda date: _first_period_session(date, "W"),
    "M": lambda date: _first_period_session(date, "M"),
    "Y": lambda date: _first_period_session(date, "Y"),
}


PERIOD_END_NORMALIZERS = {
    "D": _last_session_on_or_before,
    "W": PERIOD_START_NORMALIZERS["W"],
    "M": PERIOD_START_NORMALIZERS["M"],
    "Y": PERIOD_START_NORMALIZERS["Y"],
}


PERIOD_FETCH_START_CALCULATORS = {
    "D": _daily_fetch_start_date,
    "W": _weekly_fetch_start_date,
    "M": _monthly_fetch_start_date,
    "Y": _yearly_fetch_start_date,
}


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


def calculate_period_fetch_start_date(start_date, period, window):
    """기간과 창 크기에 따라 데이터를 가져오기 시작할 날짜를 계산한다."""

    calculator = PERIOD_FETCH_START_CALCULATORS.get(period)

    if calculator is None:
        raise ValueError(f"지원하지 않는 기간: {period}")

    return _format_date(calculator(_to_date(start_date), window))
