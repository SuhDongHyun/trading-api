from stock.domain.adapter.api_client import IApiClient
from stock.domain.stock import SlowStochasticResult, SlowStochasticValue


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
