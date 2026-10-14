from stock.domain.exceptions import NotFoundError
from stock.domain.port.stock_quote_client import StockQuoteClient
from stock.service.indicator.date_ranges import (
    calculate_daily_fetch_start_date,
    normalize_daily_start_date,
)
from stock.service.indicator.common import (
    resolve_base_indicator_date_range,
    resolve_windowed_indicator_date_range,
    calculate_ema_warmup_days,
    calculate_price_ema_seed_error,
)
from stock.service.indicator.moving_average import (
    calculate_moving_average_values,
    calculate_macd_values,
    calculate_macd_signals,
)
from stock.service.indicator.rsi import (
    calculate_rsi_values,
    calculate_rsi_signals,
)


class StockQuoteService:
    """시세 조회 결과를 기반으로 기술적 지표와 매매 참고 신호를 계산한다."""

    def __init__(self, quote_client: StockQuoteClient):
        self.quote_client = quote_client

    def get_stock_info(self, market: str, code: str):
        """시장 구분과 종목 코드로 현재 시세 정보를 조회한다."""

        return self.quote_client.get_stock_info(market, code)

    def get_daily_stock_prices(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        adjusted_price: bool = True,
    ):
        """지정 구간의 일봉 시세를 외부 API에서 조회한다."""

        valid_start_date, valid_end_date = resolve_base_indicator_date_range(
            start_date, end_date
        )

        prices = self.quote_client.get_daily_stock_prices(
            market=market,
            code=code,
            start_date=valid_start_date,
            end_date=valid_end_date,
            adjusted_price=adjusted_price,
        )
        if not prices:
            raise NotFoundError(
                f"요청 구간에 거래일 또는 시세 데이터가 없습니다: {code}"
            )
        return prices

    def get_moving_average(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        adjusted_price: bool = True,
        window: int = 5,
    ):
        """요청 구간의 이동평균 값을 반환한다."""

        fetch_start_date, valid_end_date = resolve_windowed_indicator_date_range(
            start_date, end_date, window
        )

        daily_prices = self.get_daily_stock_prices(
            market=market,
            code=code,
            start_date=fetch_start_date,
            end_date=valid_end_date,
            adjusted_price=adjusted_price,
        )

        return calculate_moving_average_values(daily_prices, window)

    def get_rsi(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        adjusted_price: bool = True,
        rsi_window: int = 14,
    ):
        """요청 구간의 RSI 지표 시계열을 계산한다."""

        fetch_start_date, valid_end_date = resolve_windowed_indicator_date_range(
            start_date, end_date, rsi_window, extra_sessions=1
        )

        daily_prices = self.get_daily_stock_prices(
            market=market,
            code=code,
            start_date=fetch_start_date,
            end_date=valid_end_date,
            adjusted_price=adjusted_price,
        )

        return calculate_rsi_values(daily_prices, rsi_window)

    def get_rsi_signal(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        adjusted_price: bool = True,
        rsi_window: int = 14,
        ema_window: int = 9,
    ):
        """RSI 값에 과매수·과매도 신호를 붙여 반환한다."""

        ema_warmup_days = calculate_ema_warmup_days(ema_window)

        fetch_start_date, valid_end_date = resolve_windowed_indicator_date_range(
            start_date, end_date, ema_warmup_days
        )

        rsi_values = self.get_rsi(
            market=market,
            code=code,
            start_date=fetch_start_date,
            end_date=valid_end_date,
            adjusted_price=adjusted_price,
            rsi_window=rsi_window,
        )

        return calculate_rsi_signals(rsi_values, ema_window, ema_warmup_days)

    def get_macd(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        adjusted_price: bool = True,
        ema_short_window: int = 12,
        ema_long_window: int = 26,
    ):
        """요청 구간 가격을 기준으로 EMA warm-up을 정해 MACD를 계산한다.

        현재가 API를 추가 호출하지 않고 요청 구간의 마지막 종가로 가격 스케일을
        잡는다. 필요한 선행 가격만 별도 조회해 요청 구간과 이어 붙인다.
        """

        valid_start_date = normalize_daily_start_date(start_date)
        prices = self.get_daily_stock_prices(
            market=market,
            code=code,
            start_date=valid_start_date,
            end_date=end_date,
            adjusted_price=adjusted_price,
        )
        latest_close_price = max(prices, key=lambda price: price.date).close_price
        max_seed_error = calculate_price_ema_seed_error(latest_close_price)
        ema_warmup_days = calculate_ema_warmup_days(
            ema_long_window, max_seed_error=max_seed_error
        )
        fetch_start_date = calculate_daily_fetch_start_date(
            valid_start_date, ema_warmup_days
        )

        if fetch_start_date < valid_start_date:
            # 상장 전 구간은 정상일 수 있어 공용 조회 메서드의 404 처리를 거치지 않는다.
            warmup_end_date = calculate_daily_fetch_start_date(valid_start_date, 2)
            warmup_prices = self.quote_client.get_daily_stock_prices(
                market,
                code,
                fetch_start_date,
                warmup_end_date,
                adjusted_price=adjusted_price,
            )
            prices = sorted(
                [*warmup_prices, *prices], key=lambda price: price.date
            )

        return calculate_macd_values(
            prices=prices,
            ema_short_window=ema_short_window,
            ema_long_window=ema_long_window,
            ema_warmup_days=ema_warmup_days,
        )

    def get_macd_signal(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        adjusted_price: bool = True,
        ema_short_window: int = 12,
        ema_long_window: int = 26,
        ema_window: int = 9,
    ):
        """MACD 값에 시그널선과 매매 신호를 붙여 반환한다."""

        ema_warmup_days = calculate_ema_warmup_days(ema_window)

        fetch_start_date, valid_end_date = resolve_windowed_indicator_date_range(
            start_date, end_date, ema_warmup_days
        )

        macd_values = self.get_macd(
            market=market,
            code=code,
            start_date=fetch_start_date,
            end_date=valid_end_date,
            adjusted_price=adjusted_price,
            ema_short_window=ema_short_window,
            ema_long_window=ema_long_window,
        )

        return calculate_macd_signals(macd_values, ema_window, ema_warmup_days)
