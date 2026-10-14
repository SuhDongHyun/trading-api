"""이동평균 지표 계산."""

import numpy as np

from stock.domain.indicator import Macd, MacdSignal, MovingAverage
from stock.domain.stock import DailyStockPrice
from stock.service.indicator.common import calculate_ema_values, crossing_signal


def calculate_moving_average_values(
    prices: list[DailyStockPrice],
    window: int,
) -> list[MovingAverage]:
    """조회한 가격 목록에서 요청 구간만 잘라 이동평균 값을 붙인다."""

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
    """공통 EMA 재귀식으로 가격의 지수 이동평균을 계산한다."""

    sorted_prices = sorted(prices, key=lambda price: price.date)
    clipped_ema_values = calculate_ema_values(
        [price.close_price for price in sorted_prices],
        ema_window,
        start_index=ema_warmup_days - 1,
    )
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
    """MACD EMA 지표 값에 교차 신호를 붙여 반환한다."""

    warmup_start = ema_warmup_days - 2
    sorted_macd_values = sorted(macd_values, key=lambda macd: macd.date)
    clipped_macd_signals = calculate_ema_values(
        [macd.value for macd in sorted_macd_values],
        ema_window,
        start_index=warmup_start,
    )
    clipped_macd_values = sorted_macd_values[warmup_start:]

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
