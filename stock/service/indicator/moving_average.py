"""이동평균 지표 계산."""

import numpy as np
from itertools import accumulate

from stock.domain.indicator import Macd, MacdSignal, MovingAverage
from stock.domain.stock import DailyStockPrice


def calculate_moving_average_values(
    prices: list[DailyStockPrice],
    window: int,
) -> list[MovingAverage]:
    """조회한 가격 목록에서 요청 구간만 잘라 이동평균 값을 붙인다."""
    if len(prices) < window:
        raise ValueError("가격 데이터 개수가 window 크기보다 작습니다.")

    sorted_prices = sorted(prices, key=lambda price: price.date)
    return [
        MovingAverage(
            date=sorted_prices[index].date,
            value=np.mean(
                [
                    price.close_price
                    for price in sorted_prices[index - window + 1 : index + 1]
                ]
            ),
        )
        for index in range(window - 1, len(sorted_prices))
    ]


def calculate_exponential_moving_average_values(
    prices: list[DailyStockPrice],
    ema_window: int,
    ema_warmup_days: int,
) -> list[MovingAverage]:
    """조회한 가격 목록에서 요청 구간만 잘라 지수 이동평균 값을 붙인다."""
    if len(prices) < ema_warmup_days:
        raise ValueError("가격 데이터 개수가 ema_warmup_days 크기보다 작습니다.")

    ema_alpha = 2 / (ema_window + 1)

    sorted_prices = sorted(prices, key=lambda price: price.date)
    clipped_ema_values = list(
        accumulate(
            (price.close_price for price in sorted_prices),
            lambda ema, price: price * ema_alpha + ema * (1 - ema_alpha),
        )
    )[ema_warmup_days - 1 :]
    clipped_prices = sorted_prices[ema_warmup_days - 1 :]

    return [
        MovingAverage(date=price.date, value=ema)
        for price, ema in zip(clipped_prices, clipped_ema_values)
    ]


def calculate_macd_values(
    prices: list[DailyStockPrice],
    ema_short_window: int,
    ema_long_window: int,
    ema_warmup_days: int,
) -> list[Macd]:
    """MACD 지표 값을 계산하여 반환한다."""

    if len(prices) < ema_warmup_days:
        raise ValueError("가격 데이터 개수가 ema_warmup_days 크기보다 작습니다.")

    ema_short = calculate_exponential_moving_average_values(
        prices, ema_short_window, ema_warmup_days
    )
    ema_long = calculate_exponential_moving_average_values(
        prices, ema_long_window, ema_warmup_days
    )

    return [
        Macd(date=short.date, value=short.value - long.value)
        for short, long in zip(ema_short, ema_long)
    ]


def calculate_macd_signals(
    macd_values: list[Macd], ema_window: int, ema_warmup_days: int
) -> list[MacdSignal]:
    """MACD EMA 지표 값에 과매수·과매도 신호를 붙여 반환한다."""

    if len(macd_values) < ema_warmup_days:
        raise ValueError("MACD 데이터 개수가 ema_warmup_days 크기보다 작습니다.")

    ema_alpha = 2 / (ema_window + 1)

    sorted_macd_values = sorted(macd_values, key=lambda macd: macd.date)
    clipped_macd_signals = list(
        accumulate(
            (macd.value for macd in sorted_macd_values),
            lambda signal, macd: macd * ema_alpha + signal * (1 - ema_alpha),
        )
    )[ema_warmup_days - 2 :]
    clipped_macd_values = sorted_macd_values[ema_warmup_days - 2 :]

    return [
        MacdSignal(
            date=curr_macd.date,
            value=curr_signal,
            signal=crossing_signal(
                prev_macd.value, curr_macd.value, prev_signal, curr_signal
            ),
        )
        for prev_macd, curr_macd, prev_signal, curr_signal in zip(
            clipped_macd_values[:-1],
            clipped_macd_values[1:],
            clipped_macd_signals[:-1],
            clipped_macd_signals[1:],
        )
    ]


def crossing_signal(
    prev_macd: float, curr_macd: float, prev_signal: float, curr_signal: float
) -> str:
    """MACD가 기준선을 상향/하향 돌파했는지에 따라 매수/매도 신호를 반환한다."""
    if prev_macd < prev_signal and curr_macd > curr_signal:
        return "buy"
    if prev_macd > prev_signal and curr_macd < curr_signal:
        return "sell"
    return "neutral"
