"""이동평균 지표 계산."""

from stock.domain.indicator import MovingAverageValue
from stock.domain.price import DailyStockPrice
from stock.service.indicator.common import simple_moving_average


def calculate_moving_average_values(
    prices: list[DailyStockPrice],
    start_date: str,
    end_date: str,
    window: int,
) -> list[MovingAverageValue]:
    """조회한 가격 목록에서 요청 구간만 잘라 이동평균 값을 붙인다."""

    sorted_prices = sorted(prices, key=lambda price: price.date)
    values: list[MovingAverageValue] = []

    for index, price in enumerate(sorted_prices):
        if price.date < start_date or price.date > end_date:
            continue

        close_prices = [item.close_price for item in sorted_prices[: index + 1]]
        moving_average = None
        if window > 0 and len(close_prices) >= window:
            moving_average = simple_moving_average(close_prices, window)
        values.append(
            MovingAverageValue(
                date=price.date,
                open_price=price.open_price,
                high_price=price.high_price,
                low_price=price.low_price,
                close_price=price.close_price,
                accumulated_volume=price.accumulated_volume,
                accumulated_trading_value=price.accumulated_trading_value,
                price_diff=price.price_diff,
                price_diff_sign=price.price_diff_sign,
                change_flag=price.change_flag,
                moving_average=moving_average,
            )
        )

    return values
