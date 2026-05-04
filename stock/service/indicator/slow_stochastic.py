"""Slow Stochastic 지표 계산."""

from stock.domain.indicator import SlowStochasticValue
from stock.domain.price import DailyStockPrice
from stock.service.indicator.common import simple_moving_average


def calculate_slow_stochastic_values(
    prices: list[DailyStockPrice],
    k_period: int,
    k_smoothing_period: int,
    d_period: int,
) -> list[SlowStochasticValue]:
    """가격 시계열에서 raw K, slow K, slow D 순서로 Stochastic 값을 만든다."""

    sorted_prices = sorted(prices, key=lambda price: price.date)
    raw_k_values: list[float] = []
    slow_k_values: list[float] = []
    values: list[SlowStochasticValue] = []

    for index, price in enumerate(sorted_prices):
        if index + 1 < k_period:
            continue

        window = sorted_prices[index + 1 - k_period : index + 1]
        lowest_low = min(item.low_price for item in window)
        highest_high = max(item.high_price for item in window)
        price_range = highest_high - lowest_low
        raw_k = (
            0.0
            if price_range == 0
            else ((price.close_price - lowest_low) / price_range) * 100
        )
        raw_k_values.append(raw_k)

        if len(raw_k_values) < k_smoothing_period:
            continue

        slow_k = simple_moving_average(raw_k_values, k_smoothing_period)
        slow_k_values.append(slow_k)

        if len(slow_k_values) < d_period:
            continue

        values.append(
            SlowStochasticValue(
                date=price.date,
                slow_k=slow_k,
                slow_d=simple_moving_average(slow_k_values, d_period),
            )
        )

    return values
