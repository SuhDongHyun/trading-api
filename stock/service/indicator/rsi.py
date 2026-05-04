"""RSI 지표와 RSI 기반 신호 계산."""

from stock.domain.indicator import RsiValue
from stock.domain.price import DailyStockPrice


def calculate_rsi_values(
    prices: list[DailyStockPrice],
    rsi_period: int,
) -> list[RsiValue]:
    """Wilder 방식의 평균 상승/하락폭을 사용해 RSI 시계열을 계산한다."""

    sorted_prices = sorted(prices, key=lambda price: price.date)
    values: list[RsiValue] = []

    if len(sorted_prices) <= rsi_period:
        return values

    changes = [
        sorted_prices[index].close_price - sorted_prices[index - 1].close_price
        for index in range(1, len(sorted_prices))
    ]
    gains = [max(change, 0.0) for change in changes]
    losses = [abs(min(change, 0.0)) for change in changes]

    average_gain = sum(gains[:rsi_period]) / rsi_period
    average_loss = sum(losses[:rsi_period]) / rsi_period
    values.append(
        RsiValue(
            date=sorted_prices[rsi_period].date,
            rsi=calculate_rsi(average_gain, average_loss),
        )
    )

    for index in range(rsi_period, len(changes)):
        average_gain = ((average_gain * (rsi_period - 1)) + gains[index]) / rsi_period
        average_loss = ((average_loss * (rsi_period - 1)) + losses[index]) / rsi_period
        values.append(
            RsiValue(
                date=sorted_prices[index + 1].date,
                rsi=calculate_rsi(average_gain, average_loss),
            )
        )

    return values


def filter_rsi_values_to_requested_range(
    values: list[RsiValue],
    start_date: str,
    end_date: str,
) -> list[RsiValue]:
    """RSI 결과 중 사용자가 요청한 날짜 범위만 남긴다."""

    return [value for value in values if start_date <= value.date <= end_date]


def calculate_rsi(average_gain: float, average_loss: float) -> float:
    """평균 상승폭과 하락폭으로 단일 RSI 값을 계산한다."""

    if average_loss == 0:
        return 100.0
    relative_strength = average_gain / average_loss
    return 100 - (100 / (1 + relative_strength))


def classify_rsi_signal(
    rsi: float,
    overbought_threshold: float,
    oversold_threshold: float,
) -> str:
    """RSI 임계값만 사용해 과매수·과매도·중립 신호를 분류한다."""

    if rsi >= overbought_threshold:
        return "OVERBOUGHT"
    if rsi <= oversold_threshold:
        return "OVERSOLD"
    return "NEUTRAL"
