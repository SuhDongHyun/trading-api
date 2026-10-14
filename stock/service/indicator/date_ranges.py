"""일봉 지표 계산에 필요한 KRX 거래일 날짜 보정 함수."""

from datetime import datetime

from common.exchange_calendar import get_krx_calendar


def _to_date(value: str):
    """YYYYMMDD 문자열을 date 객체로 변환한다."""

    return datetime.strptime(value, "%Y%m%d").date()


def _format_date(value) -> str:
    """date 또는 pandas Timestamp 값을 YYYYMMDD 문자열로 변환한다."""

    return value.strftime("%Y%m%d")


def normalize_daily_start_date(date: str) -> str:
    """시작일을 당일 또는 이후의 첫 KRX 거래일로 보정한다."""

    session = get_krx_calendar().date_to_session(_to_date(date), direction="next")
    return _format_date(session)


def normalize_daily_end_date(date: str) -> str:
    """종료일을 당일 또는 이전의 마지막 KRX 거래일로 보정한다."""

    session = get_krx_calendar().date_to_session(_to_date(date), direction="previous")
    return _format_date(session)


def calculate_daily_fetch_start_date(start_date: str, window: int) -> str:
    """시작일도 window에 포함되므로, 휴장일과 무관하게 창을 채울 window-1개 거래일 전을 반환한다."""

    session = get_krx_calendar().session_offset(_to_date(start_date), -(window - 1))
    return _format_date(session)
