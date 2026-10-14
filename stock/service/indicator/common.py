"""여러 기술적 지표 계산에서 공유하는 일봉 보조 함수."""

import math

from stock.service.indicator.date_ranges import (
    calculate_daily_fetch_start_date,
    normalize_daily_end_date,
    normalize_daily_start_date,
)

EMA_WARMUP_TOLERANCE = 0.0001
MACD_PRICE_SEED_ERROR_RATIO = 0.2
MIN_EMA_SEED_ERROR = 100.0


def calculate_ema_warmup_days(
    ema_window: int,
    max_seed_error: float = 100.0,
) -> int:
    """seed 오차가 n일 뒤 `(1-α)^n × max_seed_error`로 줄어드므로 허용 오차 이하가 되는 최소 거래일을 구한다."""

    alpha = 2 / (ema_window + 1)
    return math.ceil(
        math.log(EMA_WARMUP_TOLERANCE / max_seed_error) / math.log(1 - alpha)
    )


def calculate_price_ema_seed_error(reference_price: float | str) -> float:
    """가격 EMA warmup에 사용할 seed error 상한을 현재가 스케일로 계산한다."""

    normalized_price = float(reference_price or 0.0)
    return max(MIN_EMA_SEED_ERROR, abs(normalized_price) * MACD_PRICE_SEED_ERROR_RATIO)


def resolve_base_indicator_date_range(
    start_date: str, end_date: str
) -> tuple[str, str]:
    """조회 시작일과 종료일을 각각 KRX 거래일로 보정한다."""

    return (
        normalize_daily_start_date(start_date),
        normalize_daily_end_date(end_date),
    )


def resolve_windowed_indicator_date_range(
    start_date: str, end_date: str, window: int, extra_sessions: int = 0
) -> tuple[str, str]:
    """지표 창 앞의 거래일을 더 조회한다. RSI는 전일 대비 차분 때문에 거래일 1개가 추가로 필요하다."""

    valid_start_date = normalize_daily_start_date(start_date)
    valid_end_date = normalize_daily_end_date(end_date)
    fetch_start_date = calculate_daily_fetch_start_date(
        valid_start_date, window + extra_sessions
    )

    return fetch_start_date, valid_end_date
