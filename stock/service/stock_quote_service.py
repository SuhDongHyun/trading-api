from stock.domain.adapter.api_client import IApiClient
from stock.domain.stock import (
    RsiResult,
    RsiValue,
    SlowStochasticResult,
    SlowStochasticValue,
)


def _simple_moving_average(values: list[float], period: int) -> float:
    return sum(values[-period:]) / period


class StockQuoteService:
    def __init__(self, api_client: IApiClient):
        self.api_client = api_client

    def get_stock_info(self, market: str, code: str):
        return self.api_client.get_stock_info(market, code)

    def get_daily_stock_prices(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        period: str,
        adjusted_price: bool = True,
    ):
        return self.api_client.get_daily_stock_prices(
            market=market,
            code=code,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjusted_price=adjusted_price,
        )

    def get_slow_stochastic(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        period: str,
        adjusted_price: bool = True,
        k_period: int = 14,
        k_smoothing_period: int = 3,
        d_period: int = 3,
    ):
        daily_prices = self.get_daily_stock_prices(
            market=market,
            code=code,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjusted_price=adjusted_price,
        )
        prices = sorted(daily_prices.prices, key=lambda price: price.date)
        raw_k_values: list[float] = []
        slow_k_values: list[float] = []
        values: list[SlowStochasticValue] = []

        for index, price in enumerate(prices):
            if index + 1 < k_period:
                continue

            window = prices[index + 1 - k_period : index + 1]
            lowest_low = min(item.low_price for item in window)
            highest_high = max(item.high_price for item in window)
            price_range = highest_high - lowest_low
            raw_k = 0.0 if price_range == 0 else (
                (price.close_price - lowest_low) / price_range
            ) * 100
            raw_k_values.append(raw_k)

            if len(raw_k_values) < k_smoothing_period:
                continue

            slow_k = _simple_moving_average(raw_k_values, k_smoothing_period)
            slow_k_values.append(slow_k)

            if len(slow_k_values) < d_period:
                continue

            values.append(
                SlowStochasticValue(
                    date=price.date,
                    slow_k=slow_k,
                    slow_d=_simple_moving_average(slow_k_values, d_period),
                )
            )

        return SlowStochasticResult(summary=daily_prices.summary, values=values)

    def get_rsi(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        period: str,
        adjusted_price: bool = True,
        rsi_period: int = 14,
    ):
        daily_prices = self.get_daily_stock_prices(
            market=market,
            code=code,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjusted_price=adjusted_price,
        )
        prices = sorted(daily_prices.prices, key=lambda price: price.date)
        values: list[RsiValue] = []

        if len(prices) <= rsi_period:
            return RsiResult(summary=daily_prices.summary, values=values)

        changes = [
            prices[index].close_price - prices[index - 1].close_price
            for index in range(1, len(prices))
        ]
        gains = [max(change, 0.0) for change in changes]
        losses = [abs(min(change, 0.0)) for change in changes]

        average_gain = sum(gains[:rsi_period]) / rsi_period
        average_loss = sum(losses[:rsi_period]) / rsi_period
        values.append(
            RsiValue(
                date=prices[rsi_period].date,
                rsi=self._calculate_rsi(average_gain, average_loss),
            )
        )

        for index in range(rsi_period, len(changes)):
            average_gain = (
                (average_gain * (rsi_period - 1)) + gains[index]
            ) / rsi_period
            average_loss = (
                (average_loss * (rsi_period - 1)) + losses[index]
            ) / rsi_period
            values.append(
                RsiValue(
                    date=prices[index + 1].date,
                    rsi=self._calculate_rsi(average_gain, average_loss),
                )
            )

        return RsiResult(summary=daily_prices.summary, values=values)

    def _calculate_rsi(self, average_gain: float, average_loss: float) -> float:
        if average_loss == 0:
            return 100.0
        relative_strength = average_gain / average_loss
        return 100 - (100 / (1 + relative_strength))
