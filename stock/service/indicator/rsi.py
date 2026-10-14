"""RSI 지표와 RSI 기반 신호 계산."""

import pandas as pd

from stock.domain.indicator import Rsi, RsiSignal
from stock.domain.stock import DailyStockPrice
from stock.service.indicator.common import calculate_ema_values, crossing_signal


def calculate_rsi_values(
    prices: list[DailyStockPrice],
    rsi_period: int,
) -> list[Rsi]:
    """단순 이동평균 RSI를 계산하고 손실이 없는 창의 경계값을 정의한다."""

    sorted_prices = sorted(prices, key=lambda price: price.date)
    sorted_dates = [price.date for price in sorted_prices]
    close = pd.Series([price.close_price for price in sorted_prices], dtype=float)

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=rsi_period).mean()
    avg_loss = loss.rolling(window=rsi_period).mean()
    # 손실만 없는 창은 공식상 100이고, 상승·하락이 모두 없는 창은 중립값 50이다.
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    no_movement = avg_gain.eq(0) & avg_loss.eq(0)
    rsi = rsi.mask(no_movement, 50.0)

    return [
        Rsi(date=date, value=value)
        for date, value in list(zip(sorted_dates, rsi))[rsi_period:]
    ]


def calculate_rsi_signals(
    rsi_values: list[Rsi], ema_window: int, ema_warmup_days: int
) -> list[RsiSignal]:
    """RSI EMA 지표 값에 교차 신호를 붙여 반환한다."""

    warmup_start = ema_warmup_days - 2
    sorted_rsi_values = sorted(rsi_values, key=lambda rsi: rsi.date)
    clipped_rsi_signals = calculate_ema_values(
        [rsi.value for rsi in sorted_rsi_values],
        ema_window,
        start_index=warmup_start,
    )
    clipped_rsi_values = sorted_rsi_values[warmup_start:]

    return [
        RsiSignal(
            date=curr_rsi.date,
            value=curr_signal,
            signal=crossing_signal(
                prev_rsi.value, curr_rsi.value, prev_signal, curr_signal
            ),
        )
        for prev_rsi, curr_rsi, prev_signal, curr_signal in zip(
            clipped_rsi_values[:-1],
            clipped_rsi_values[1:],
            clipped_rsi_signals[:-1],
            clipped_rsi_signals[1:],
        )
    ]
