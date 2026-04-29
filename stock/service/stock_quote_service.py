from datetime import datetime, timedelta

from stock.domain.adapter.api_client import IApiClient
from stock.domain.stock import (
    DailyStockPrice,
    MovingAverageResult,
    MovingAverageValue,
    OverboughtOversoldResult,
    OverboughtOversoldValue,
    RsiResult,
    RsiSignalResult,
    RsiSignalValue,
    RsiValue,
    SlowStochasticResult,
    SlowStochasticValue,
)


def _simple_moving_average(values: list[float], period: int) -> float:
    """입력 목록의 마지막 period개 값으로 단순 이동평균을 계산한다."""

    return sum(values[-period:]) / period


def _calculate_history_lookup_start_date(
    start_date: str, window: int, period: str
) -> str:
    """이동평균 계산에 필요한 선행 시세를 넉넉히 조회할 시작일을 추정한다."""

    days_by_period = {
        "D": 2,
        "W": 7,
        "M": 31,
        "Y": 366,
    }
    days_per_window = days_by_period.get(period, 2)
    date = datetime.strptime(start_date, "%Y%m%d").date()
    return (date - timedelta(days=window * days_per_window)).strftime("%Y%m%d")


def _previous_date(date: str) -> str:
    """YYYYMMDD 문자열 기준으로 하루 전 날짜를 반환한다."""

    return (datetime.strptime(date, "%Y%m%d").date() - timedelta(days=1)).strftime(
        "%Y%m%d"
    )


class StockQuoteService:
    """시세 조회 결과를 기반으로 기술적 지표와 매매 참고 신호를 계산한다."""

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
        return SlowStochasticResult(
            summary=daily_prices.summary,
            values=self._calculate_slow_stochastic_values(
                daily_prices.prices,
                k_period=k_period,
                k_smoothing_period=k_smoothing_period,
                d_period=d_period,
            ),
        )

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
        if rsi_period <= 0:
            raise ValueError("rsi_period must be positive")

        daily_prices = self._fetch_rsi_price_history(
            market=market,
            code=code,
            end_date=end_date,
            period=period,
            adjusted_price=adjusted_price,
            rsi_period=rsi_period,
            start_date=start_date,
        )
        return RsiResult(
            summary=daily_prices.summary,
            values=self._filter_rsi_values_to_requested_range(
                self._calculate_rsi_values(daily_prices.prices, rsi_period),
                start_date=start_date,
                end_date=end_date,
            ),
        )

    def get_rsi_signal(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        period: str,
        adjusted_price: bool = True,
        rsi_period: int = 14,
        overbought_threshold: float = 70.0,
        oversold_threshold: float = 30.0,
    ):
        indicator = self.get_rsi(
            market=market,
            code=code,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjusted_price=adjusted_price,
            rsi_period=rsi_period,
        )
        return RsiSignalResult(
            summary=indicator.summary,
            values=[
                RsiSignalValue(
                    date=value.date,
                    rsi=value.rsi,
                    signal=self._classify_rsi_signal(
                        rsi=value.rsi,
                        overbought_threshold=overbought_threshold,
                        oversold_threshold=oversold_threshold,
                    ),
                )
                for value in indicator.values
            ],
        )

    def get_overbought_oversold(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        period: str,
        adjusted_price: bool = True,
        rsi_period: int = 14,
        stochastic_k_period: int = 14,
        stochastic_k_smoothing_period: int = 3,
        stochastic_d_period: int = 3,
        rsi_overbought_threshold: float = 70.0,
        rsi_oversold_threshold: float = 30.0,
        stochastic_overbought_threshold: float = 80.0,
        stochastic_oversold_threshold: float = 20.0,
    ):
        daily_prices = self.get_daily_stock_prices(
            market=market,
            code=code,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjusted_price=adjusted_price,
        )
        rsi_by_date = {
            value.date: value
            for value in self._calculate_rsi_values(daily_prices.prices, rsi_period)
        }
        stochastic_by_date = {
            value.date: value
            for value in self._calculate_slow_stochastic_values(
                daily_prices.prices,
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
                    signal=self._classify_overbought_oversold(
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

        return OverboughtOversoldResult(summary=daily_prices.summary, values=values)

    def _calculate_slow_stochastic_values(
        self,
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

        return values

    def _calculate_rsi_values(
        self,
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
                    date=sorted_prices[index + 1].date,
                    rsi=self._calculate_rsi(average_gain, average_loss),
                )
            )

        return values

    def _fetch_rsi_price_history(
        self,
        market: str,
        code: str,
        end_date: str,
        period: str,
        adjusted_price: bool,
        rsi_period: int,
        start_date: str,
    ):
        """요청 시작일의 RSI까지 계산되도록 필요한 선행 가격을 추가 조회한다."""

        prices_by_date: dict[str, DailyStockPrice] = {}
        previous_oldest_date = None
        initial_start_date = _calculate_history_lookup_start_date(
            start_date=start_date,
            window=rsi_period,
            period=period,
        )
        daily_prices = self.get_daily_stock_prices(
            market=market,
            code=code,
            start_date=initial_start_date,
            end_date=end_date,
            period=period,
            adjusted_price=adjusted_price,
        )
        for price in daily_prices.prices:
            prices_by_date[price.date] = price

        while daily_prices.prices:
            sorted_prices = sorted(prices_by_date.values(), key=lambda price: price.date)
            if self._has_enough_rsi_history(
                prices=sorted_prices,
                start_date=start_date,
                rsi_period=rsi_period,
            ):
                break

            oldest_date = sorted_prices[0].date
            if oldest_date >= start_date or oldest_date == previous_oldest_date:
                break
            previous_oldest_date = oldest_date
            chunk_end_date = _previous_date(oldest_date)
            chunk_start_date = _calculate_history_lookup_start_date(
                start_date=chunk_end_date,
                window=rsi_period,
                period=period,
            )
            daily_prices = self.get_daily_stock_prices(
                market=market,
                code=code,
                start_date=chunk_start_date,
                end_date=chunk_end_date,
                period=period,
                adjusted_price=adjusted_price,
            )
            if not daily_prices.prices:
                break

            for price in daily_prices.prices:
                prices_by_date[price.date] = price

        daily_prices.prices = sorted(prices_by_date.values(), key=lambda price: price.date)
        return daily_prices

    def _has_enough_rsi_history(
        self,
        prices: list[DailyStockPrice],
        start_date: str,
        rsi_period: int,
    ) -> bool:
        """첫 요청 날짜 앞에 RSI period만큼의 가격 이력이 모였는지 확인한다."""

        sorted_prices = sorted(prices, key=lambda price: price.date)
        first_requested_index = next(
            (
                index
                for index, price in enumerate(sorted_prices)
                if price.date >= start_date
            ),
            None,
        )
        if first_requested_index is None:
            return True
        return first_requested_index >= rsi_period

    def _filter_rsi_values_to_requested_range(
        self,
        values: list[RsiValue],
        start_date: str,
        end_date: str,
    ) -> list[RsiValue]:
        return [
            value
            for value in values
            if start_date <= value.date <= end_date
        ]

    def get_moving_average(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        period: str,
        adjusted_price: bool = True,
        window: int = 20,
    ):
        if window <= 0:
            raise ValueError("window must be positive")

        daily_prices = self._fetch_moving_average_price_history(
            market=market,
            code=code,
            end_date=end_date,
            period=period,
            adjusted_price=adjusted_price,
            start_date=start_date,
            window=window,
        )
        return MovingAverageResult(
            summary=daily_prices.summary,
            values=self._calculate_moving_average_values(
                daily_prices.prices,
                start_date=start_date,
                end_date=end_date,
                window=window,
            ),
        )

    def _fetch_moving_average_price_history(
        self,
        market: str,
        code: str,
        end_date: str,
        period: str,
        adjusted_price: bool,
        window: int,
        start_date: str,
    ):
        """요청 시작일의 이동평균까지 계산되도록 과거 가격을 추가 조회한다."""

        prices_by_date: dict[str, DailyStockPrice] = {}
        chunk_end_date = end_date
        previous_oldest_date = None
        daily_prices = None

        while True:
            chunk_start_date = _calculate_history_lookup_start_date(
                start_date=chunk_end_date,
                window=window,
                period=period,
            )
            daily_prices = self.get_daily_stock_prices(
                market=market,
                code=code,
                start_date=chunk_start_date,
                end_date=chunk_end_date,
                period=period,
                adjusted_price=adjusted_price,
            )
            if not daily_prices.prices:
                break

            for price in daily_prices.prices:
                prices_by_date[price.date] = price

            sorted_prices = sorted(prices_by_date.values(), key=lambda price: price.date)
            if self._has_enough_moving_average_history(
                prices=sorted_prices,
                start_date=start_date,
                window=window,
            ):
                break

            oldest_date = sorted_prices[0].date
            if oldest_date == previous_oldest_date:
                break
            previous_oldest_date = oldest_date
            chunk_end_date = _previous_date(oldest_date)

        if daily_prices is None:
            return self.get_daily_stock_prices(
                market=market,
                code=code,
                start_date=start_date,
                end_date=end_date,
                period=period,
                adjusted_price=adjusted_price,
            )

        daily_prices.prices = sorted(prices_by_date.values(), key=lambda price: price.date)
        return daily_prices

    def _has_enough_moving_average_history(
        self,
        prices: list[DailyStockPrice],
        start_date: str,
        window: int,
    ) -> bool:
        """요청 구간 첫 날짜 앞에 window만큼의 가격 이력이 확보됐는지 확인한다."""

        sorted_prices = sorted(prices, key=lambda price: price.date)
        first_requested_index = next(
            (
                index
                for index, price in enumerate(sorted_prices)
                if price.date >= start_date
            ),
            None,
        )
        if first_requested_index is None:
            return True
        return first_requested_index + 1 >= window

    def _calculate_moving_average_values(
        self,
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

            close_prices = [
                item.close_price for item in sorted_prices[: index + 1]
            ]
            moving_average = None
            if window > 0 and len(close_prices) >= window:
                moving_average = _simple_moving_average(close_prices, window)
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

    def _calculate_rsi(self, average_gain: float, average_loss: float) -> float:
        """평균 상승폭과 하락폭으로 단일 RSI 값을 계산한다."""

        if average_loss == 0:
            return 100.0
        relative_strength = average_gain / average_loss
        return 100 - (100 / (1 + relative_strength))

    def _classify_overbought_oversold(
        self,
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

    def _classify_rsi_signal(
        self,
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
