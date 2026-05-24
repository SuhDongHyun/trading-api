"""RSI 지표와 RSI 기반 신호 계산."""

import pandas as pd
from itertools import accumulate

from stock.domain.indicator import Rsi, RsiSignal
from stock.domain.price import DailyStockPrice


def calculate_rsi_values(
    prices: list[DailyStockPrice],
    rsi_period: int,
) -> list[Rsi]:
    """조회한 가격 목록에서 요청 구간만 잘라 RSI 값을 붙인다."""
    if len(prices) < rsi_period + 1:
        raise ValueError("가격 데이터 개수가 RSI 계산에 필요한 기간보다 작습니다.")

    sorted_prices = sorted(prices, key=lambda price: price.date)
    sorted_dates = [price.date for price in sorted_prices]
    close = pd.Series([price.close_price for price in sorted_prices], dtype=float)

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=rsi_period).mean()
    avg_loss = loss.rolling(window=rsi_period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return [
        Rsi(date=date, value=value)
        for date, value in list(zip(sorted_dates, rsi))[rsi_period:]
    ]


def calculate_rsi_signals(
    rsi_values: list[Rsi], ema_window: int, ema_warmup_days: int
) -> list[RsiSignal]:
    """RSI EMA 지표 값에 과매수·과매도 신호를 붙여 반환한다."""

    if len(rsi_values) < ema_warmup_days:
        raise ValueError("RSI 값 개수가 ema_warmup_days 크기보다 작습니다.")

    ema_alpha = 2 / (ema_window + 1)

    sorted_rsi_values = sorted(rsi_values, key=lambda rsi: rsi.date)
    clipped_rsi_signals = list(
        accumulate(
            (rsi.value for rsi in sorted_rsi_values),
            lambda signal, rsi: rsi * ema_alpha + signal * (1 - ema_alpha),
        )
    )[ema_warmup_days - 2 :]
    clipped_rsi_values = sorted_rsi_values[ema_warmup_days - 2 :]

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


def crossing_signal(
    prev_rsi: float, curr_rsi: float, prev_signal: float, curr_signal: float
) -> str:
    """RSI가 기준선을 상향/하향 돌파했는지에 따라 매수/매도 신호를 반환한다."""
    if prev_rsi < prev_signal and curr_rsi > curr_signal:
        return "buy"
    if prev_rsi > prev_signal and curr_rsi < curr_signal:
        return "sell"
    return "neutral"
