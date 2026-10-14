"""여러 기술적 지표 계산에서 공유하는 일봉 보조 함수."""

import math
from itertools import accumulate

from stock.domain.indicator import Signal
from stock.service.indicator.date_ranges import (
    calculate_daily_fetch_start_date,
    normalize_daily_end_date,
    normalize_daily_start_date,
)

EMA_WARMUP_TOLERANCE = 0.0001
MACD_PRICE_SEED_ERROR_RATIO = 0.2
MIN_EMA_SEED_ERROR = 100.0


def calculate_ema_values(
    values: list[float], ema_window: int, start_index: int = 0
) -> list[float]:
    """EMA 재귀식을 한 곳에서 적용하고 지정한 warm-up 구간을 제외한다."""

    ema_alpha = 2 / (ema_window + 1)
    values_with_warmup = accumulate(
        values,
        lambda ema, value: value * ema_alpha + ema * (1 - ema_alpha),
    )
    return list(values_with_warmup)[start_index:]


def crossing_signal(
    previous_value: float,
    current_value: float,
    previous_average: float,
    current_average: float,
) -> Signal:
    """값 계열이 EMA를 상향·하향 돌파할 때만 매수·매도 신호를 낸다."""

    if previous_value < previous_average and current_value > current_average:
        return "buy"
    if previous_value > previous_average and current_value < current_average:
        return "sell"
    return "neutral"


def calculate_ema_warmup_days(
    ema_window: int,
    max_seed_error: float = 100.0,
) -> int:
    """seed 오차가 n일 뒤 `(1-α)^n × max_seed_error`로 줄어드므로 허용 오차 이하가 되는 최소 거래일을 구한다."""

    alpha = 2 / (ema_window + 1)
    return math.ceil(
        math.log(EMA_WARMUP_TOLERANCE / max_seed_error) / math.log(1 - alpha)
    )


def calculate_price_ema_seed_error(reference_price: float) -> float:
    """요청 구간 종가 스케일의 20%를 seed 오차 상한으로 둔다.

    수정주가 설정을 포함해 실제 EMA에 사용할 동일 시계열의 가격을 기준으로 한다.
    """

    return max(
        MIN_EMA_SEED_ERROR,
        abs(reference_price) * MACD_PRICE_SEED_ERROR_RATIO,
    )


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
