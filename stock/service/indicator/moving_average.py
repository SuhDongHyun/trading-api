"""이동평균 지표 계산."""

import numpy as np
from itertools import accumulate

from stock.domain.indicator import MovingAverage
from stock.domain.price import DailyStockPrice


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
