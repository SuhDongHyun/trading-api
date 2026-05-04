from datetime import datetime, timedelta

from stock.domain.adapter.api_client import IApiClient
from stock.domain.indicator import (
    MovingAverageResult,
    OverboughtOversoldResult,
    RsiResult,
    RsiSignalResult,
    RsiSignalValue,
    SlowStochasticResult,
)
from stock.domain.price import DailyStockPrice, DailyStockPriceResult
from stock.service.indicator.moving_average import calculate_moving_average_values
from stock.service.indicator.overbought_oversold import (
    calculate_overbought_oversold_values,
)
from stock.service.indicator.rsi import (
    calculate_rsi_values,
    classify_rsi_signal,
    filter_rsi_values_to_requested_range,
)
from stock.service.indicator.slow_stochastic import calculate_slow_stochastic_values


def calculate_history_lookup_start_date(
    start_date: str, window: int, period: str
) -> str:
    """지표 계산에 필요한 선행 시세를 넉넉히 조회할 시작일을 추정한다."""

    days_by_period = {
        "D": 2,
        "W": 7,
        "M": 31,
        "Y": 366,
    }
    days_per_window = days_by_period.get(period, 2)
    date = datetime.strptime(start_date, "%Y%m%d").date()
    return (date - timedelta(days=window * days_per_window)).strftime("%Y%m%d")


def previous_date(date: str) -> str:
    """YYYYMMDD 문자열 기준으로 하루 전 날짜를 반환한다."""

    return (datetime.strptime(date, "%Y%m%d").date() - timedelta(days=1)).strftime(
        "%Y%m%d"
    )


class StockQuoteService:
    """시세 조회 결과를 기반으로 기술적 지표와 매매 참고 신호를 계산한다."""

    def __init__(self, api_client: IApiClient):
        """시세 데이터를 가져올 API 클라이언트를 주입받는다."""

        self.api_client = api_client

    def get_stock_info(self, market: str, code: str):
        """시장 구분과 종목 코드로 현재 시세 정보를 조회한다."""

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
        """지정 구간의 일봉 시세를 외부 API에서 조회한다."""

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
        """일봉 가격으로 Slow Stochastic 지표를 계산한다."""

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
            values=calculate_slow_stochastic_values(
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
        """요청 구간의 RSI 지표 시계열을 계산한다."""

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
            values=filter_rsi_values_to_requested_range(
                calculate_rsi_values(daily_prices.prices, rsi_period),
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
        """RSI 값에 과매수·과매도 신호를 붙여 반환한다."""

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
                    signal=classify_rsi_signal(
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
        """RSI와 Slow Stochastic을 조합해 과매수·과매도 신호를 만든다."""

        daily_prices = self.get_daily_stock_prices(
            market=market,
            code=code,
            start_date=start_date,
            end_date=end_date,
            period=period,
            adjusted_price=adjusted_price,
        )

        return OverboughtOversoldResult(
            summary=daily_prices.summary,
            values=calculate_overbought_oversold_values(
                daily_prices.prices,
                rsi_period=rsi_period,
                stochastic_k_period=stochastic_k_period,
                stochastic_k_smoothing_period=stochastic_k_smoothing_period,
                stochastic_d_period=stochastic_d_period,
                rsi_overbought_threshold=rsi_overbought_threshold,
                rsi_oversold_threshold=rsi_oversold_threshold,
                stochastic_overbought_threshold=stochastic_overbought_threshold,
                stochastic_oversold_threshold=stochastic_oversold_threshold,
            ),
        )

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
        """요청 구간의 이동평균 값을 일봉 시세에 붙여 반환한다."""

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
            values=calculate_moving_average_values(
                daily_prices.prices,
                start_date=start_date,
                end_date=end_date,
                window=window,
            ),
        )

    def _fetch_rsi_price_history(
        self,
        market: str,
        code: str,
        end_date: str,
        period: str,
        adjusted_price: bool,
        rsi_period: int,
        start_date: str,
    ) -> DailyStockPriceResult:
        """요청 시작일의 RSI까지 계산되도록 필요한 선행 가격을 추가 조회한다."""

        prices_by_date: dict[str, DailyStockPrice] = {}
        previous_oldest_date = None
        initial_start_date = calculate_history_lookup_start_date(
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
            chunk_end_date = previous_date(oldest_date)
            chunk_start_date = calculate_history_lookup_start_date(
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

    def _fetch_moving_average_price_history(
        self,
        market: str,
        code: str,
        end_date: str,
        period: str,
        adjusted_price: bool,
        window: int,
        start_date: str,
    ) -> DailyStockPriceResult:
        """요청 시작일의 이동평균까지 계산되도록 과거 가격을 추가 조회한다."""

        prices_by_date: dict[str, DailyStockPrice] = {}
        chunk_end_date = end_date
        previous_oldest_date = None
        daily_prices = None

        while True:
            chunk_start_date = calculate_history_lookup_start_date(
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
            chunk_end_date = previous_date(oldest_date)

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
