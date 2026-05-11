"""이동평균 지표 계산."""

import numpy as np

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
