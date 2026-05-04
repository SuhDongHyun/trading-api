"""RSI와 Slow Stochastic을 조합한 과매수·과매도 신호 계산."""

from stock.domain.indicator import OverboughtOversoldValue
from stock.domain.price import DailyStockPrice
from stock.service.indicator.rsi import calculate_rsi_values
from stock.service.indicator.slow_stochastic import calculate_slow_stochastic_values


def calculate_overbought_oversold_values(
    prices: list[DailyStockPrice],
    rsi_period: int,
    stochastic_k_period: int,
    stochastic_k_smoothing_period: int,
    stochastic_d_period: int,
    rsi_overbought_threshold: float,
    rsi_oversold_threshold: float,
    stochastic_overbought_threshold: float,
    stochastic_oversold_threshold: float,
) -> list[OverboughtOversoldValue]:
    """RSI와 Stochastic 결과를 날짜별로 합쳐 복합 신호를 만든다."""

    rsi_by_date = {
        value.date: value for value in calculate_rsi_values(prices, rsi_period)
    }
    stochastic_by_date = {
        value.date: value
        for value in calculate_slow_stochastic_values(
            prices,
            k_period=stochastic_k_period,
            k_smoothing_period=stochastic_k_smoothing_period,
            d_period=stochastic_d_period,
        )
    }

    values: list[OverboughtOversoldValue] = []
    for date in sorted(rsi_by_date.keys() & stochastic_by_date.keys()):
        rsi = rsi_by_date[date]
        stochastic = stochastic_by_date[date]
        values.append(
            OverboughtOversoldValue(
                date=date,
                rsi=rsi.rsi,
                slow_k=stochastic.slow_k,
                slow_d=stochastic.slow_d,
                signal=classify_overbought_oversold(
                    rsi=rsi.rsi,
                    slow_k=stochastic.slow_k,
                    slow_d=stochastic.slow_d,
                    rsi_overbought_threshold=rsi_overbought_threshold,
                    rsi_oversold_threshold=rsi_oversold_threshold,
                    stochastic_overbought_threshold=stochastic_overbought_threshold,
                    stochastic_oversold_threshold=stochastic_oversold_threshold,
                ),
            )
        )

    return values


def classify_overbought_oversold(
    rsi: float,
    slow_k: float,
    slow_d: float,
    rsi_overbought_threshold: float,
    rsi_oversold_threshold: float,
    stochastic_overbought_threshold: float,
    stochastic_oversold_threshold: float,
) -> str:
    """RSI 또는 Stochastic 임계값을 넘는지에 따라 신호를 분류한다."""

    if (
        rsi >= rsi_overbought_threshold
        or slow_k >= stochastic_overbought_threshold
        or slow_d >= stochastic_overbought_threshold
    ):
        return "OVERBOUGHT"
    if (
        rsi <= rsi_oversold_threshold
        or slow_k <= stochastic_oversold_threshold
        or slow_d <= stochastic_oversold_threshold
    ):
        return "OVERSOLD"
    return "NEUTRAL"
