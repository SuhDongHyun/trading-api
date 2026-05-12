from stock.domain.adapter.api_client import IApiClient
from stock.service.indicator.common import (
    resolve_indicator_date_range,
    calculate_ema_warmup_days,
)
from stock.service.indicator.moving_average import (
    calculate_moving_average_values,
)
from stock.service.indicator.rsi import (
    calculate_rsi_values,
    calculate_rsi_signals,
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

    def get_moving_average(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        period: str,
        adjusted_price: bool = True,
        window: int = 5,
    ):
        """요청 구간의 이동평균 값을 반환한다."""

        if window <= 0:
            raise ValueError("window must be positive")

        fetch_start_date, valid_end_date = resolve_indicator_date_range(
            start_date, end_date, period, window
        )

        period_prices = self.get_daily_stock_prices(
            market=market,
            code=code,
            start_date=fetch_start_date,
            end_date=valid_end_date,
            period=period,
            adjusted_price=adjusted_price,
        )

        return calculate_moving_average_values(period_prices, window)

    def get_rsi(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        period: str,
        adjusted_price: bool = True,
        rsi_window: int = 14,
    ):
        """요청 구간의 RSI 지표 시계열을 계산한다."""

        if rsi_window <= 0:
            raise ValueError("window must be positive")

        fetch_start_date, valid_end_date = resolve_indicator_date_range(
            start_date, end_date, period, rsi_window, extra_periods=1
        )

        period_prices = self.get_daily_stock_prices(
            market=market,
            code=code,
            start_date=fetch_start_date,
            end_date=valid_end_date,
            period=period,
            adjusted_price=adjusted_price,
        )

        return calculate_rsi_values(period_prices, rsi_window)

    def get_rsi_signal(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        period: str,
        adjusted_price: bool = True,
        rsi_window: int = 14,
        ema_window: int = 9,
    ):
        """RSI 값에 과매수·과매도 신호를 붙여 반환한다."""

        ema_warmup_days = calculate_ema_warmup_days(ema_window)

        fetch_start_date, valid_end_date = resolve_indicator_date_range(
            start_date, end_date, period, ema_warmup_days
        )

        rsi_values = self.get_rsi(
            market=market,
            code=code,
            start_date=fetch_start_date,
            end_date=valid_end_date,
            period=period,
            adjusted_price=adjusted_price,
            rsi_window=rsi_window,
        )

        return calculate_rsi_signals(rsi_values, ema_window, ema_warmup_days)
