from pydantic import Field

from stock.domain.indicator import Signal
from stock.interface.schema.common import DateRangeRequest, RequestModel, ResponseModel


class StockQuoteRequest(RequestModel):
    """주식 시세 조회 공통 요청 모델."""

    market: str = Field(
        default="J", description="시장 구분 코드. 국내 주식은 J를 사용합니다."
    )
    code: str = Field(
        default="005930", description="종목 코드. 기본값은 삼성전자 005930입니다."
    )


class HistoricalStockQuoteRequest(StockQuoteRequest, DateRangeRequest):
    """기간별 주식 시세 조회 공통 요청 모델."""

    adjusted_price: bool = Field(default=True, description="수정주가 반영 여부입니다.")


class StockInfoResponse(ResponseModel):
    """현재가 조회 API 응답 스키마."""

    market_name: str
    code: str
    name: str
    industry: str
    per: float
    pbr: float
    eps: float
    bps: float
    open_price: float
    current_price: float
    previous_price: float
    highest_price: float
    lowest_price: float
    upper_limit_price: float
    lower_limit_price: float
    current_volume: int
    previous_volume: int
    current_trading_value: float
    price_diff: float
    price_diff_rate: float


class DailyStockPriceResponse(ResponseModel):
    """특정 거래일의 일봉 가격 응답."""

    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    accumulated_volume: int
    accumulated_trading_value: float
    price_diff: float
    price_diff_sign: str
    change_flag: str


class MovingAverageRequest(HistoricalStockQuoteRequest):
    """이동평균 계산 요청 파라미터."""

    window: int = Field(default=20, ge=1, description="이동평균 계산 기간입니다.")


class MovingAverageResponse(ResponseModel):
    """특정 날짜의 가격과 이동평균 값 응답."""

    date: str
    moving_average: float = Field(validation_alias="value")


class RsiRequest(HistoricalStockQuoteRequest):
    """RSI 계산 요청 파라미터."""

    rsi_window: int = Field(default=14, ge=1, description="RSI 계산 기간입니다.")


class RsiResponse(ResponseModel):
    """특정 날짜의 RSI 값 응답."""

    date: str
    rsi: float = Field(validation_alias="value")


class RsiSignalRequest(RsiRequest):
    """RSI 신호 계산 요청 파라미터."""

    ema_window: int = Field(
        default=9, ge=2, description="RSI signal EMA 계산 기간입니다."
    )


class RsiSignalResponse(ResponseModel):
    """특정 날짜의 RSI EMA 지표 값과 신호 응답."""

    date: str
    rsi_ema: float = Field(validation_alias="value")
    signal: Signal


class MacdRequest(HistoricalStockQuoteRequest):
    """MACD 계산 요청 파라미터."""

    ema_short_window: int = Field(
        default=12, ge=2, description="MACD 단기 EMA 계산 기간입니다."
    )
    ema_long_window: int = Field(
        default=26, ge=2, description="MACD 장기 EMA 계산 기간입니다."
    )


class MacdSignalRequest(MacdRequest):
    """MACD 신호 계산에 필요한 signal EMA 창을 받는다."""

    ema_window: int = Field(
        default=9, ge=2, description="MACD signal EMA 계산 기간입니다."
    )


class MacdResponse(ResponseModel):
    """특정 날짜의 MACD 값 응답."""

    date: str
    macd: float = Field(validation_alias="value")


class MacdSignalResponse(ResponseModel):
    """특정 날짜의 MACD EMA 지표 값과 신호 응답."""

    date: str
    macd_ema: float = Field(validation_alias="value")
    signal: Signal
