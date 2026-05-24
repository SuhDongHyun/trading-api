"""여러 기술적 지표 계산에서 공유하는 보조 함수."""

import math

from stock.service.indicator.date_ranges import (
    calculate_period_fetch_start_date,
    normalize_period_end,
    normalize_period_start,
)

EMA_WARMUP_TOLERANCE_BY_PERIOD = {
    "D": 0.0001,
    "W": 0.0001,
    "M": 0.00001,
    "Y": 0.000001,
}
MACD_PRICE_SEED_ERROR_RATIO = 0.2
MIN_EMA_SEED_ERROR = 100.0


def calculate_indicator_fetch_start_date(start_date, period, window):
    """기간과 창 크기에 따라 데이터를 가져오기 시작할 날짜를 계산한다."""

    return calculate_period_fetch_start_date(start_date, period, window)


def calculate_ema_warmup_days(
    ema_window: int,
    period: str,
    max_seed_error: float = 100.0,
) -> int:
    alpha = 2 / (ema_window + 1)
    tolerance = EMA_WARMUP_TOLERANCE_BY_PERIOD.get(period, 0.0001)
    return math.ceil(math.log(tolerance / max_seed_error) / math.log(1 - alpha))


def calculate_price_ema_seed_error(reference_price: float | str) -> float:
    """가격 EMA warmup에 사용할 seed error 상한을 현재가 스케일로 계산한다."""

    normalized_price = float(reference_price or 0.0)
    return max(MIN_EMA_SEED_ERROR, abs(normalized_price) * MACD_PRICE_SEED_ERROR_RATIO)


def resolve_base_indicator_date_range(
    start_date: str, end_date: str, period: str
) -> tuple[str, str]:
    """기본 지표 계산에 필요한 날짜 범위를 정규화하고 계산한다."""

    valid_start_date = normalize_period_start(start_date, period)
    valid_end_date = normalize_period_end(end_date, period)

    return valid_start_date, valid_end_date


def resolve_windowed_indicator_date_range(
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
