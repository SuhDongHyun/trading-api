from typing import Literal
from pydantic import BaseModel, Field


PeriodCode = Literal["D", "W", "M", "Y"]


class StockInfoRequest(BaseModel):
    """현재가 조회에 필요한 시장 구분과 종목 코드."""

    market: str = Field(
        default="J", description="시장 구분 코드. 국내 주식은 J를 사용합니다."
    )
    code: str = Field(
        default="005930", description="종목 코드. 기본값은 삼성전자 005930입니다."
    )


class StockInfoResponse(BaseModel):
    """현재가 조회 API 응답 스키마."""

    market_name: str
    code: str
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


class DailyStockPriceRequest(BaseModel):
    """일봉 조회 요청 파라미터."""

    market: str = Field(
        default="J", description="시장 구분 코드. 국내 주식은 J를 사용합니다."
    )
    code: str = Field(
        default="005930", description="종목 코드. 기본값은 삼성전자 005930입니다."
    )
    start_date: str = Field(
        default="20260101",
        description="조회 시작일입니다.",
    )
    end_date: str = Field(
        default="20260107",
        description="조회 종료일입니다.",
    )
    period: PeriodCode = Field(
        default="D",
        description="기간 구분 코드. D(일), W(주), M(월), Y(년) 중 하나입니다.",
    )
    adjusted_price: bool = Field(default=True, description="수정주가 반영 여부입니다.")


class DailyStockPriceResponse(BaseModel):
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


class MovingAverageRequest(BaseModel):
    """이동평균 계산 요청 파라미터."""

    market: str = Field(
        default="J", description="시장 구분 코드. 국내 주식은 J를 사용합니다."
    )
    code: str = Field(
        default="005930", description="종목 코드. 기본값은 삼성전자 005930입니다."
    )
    start_date: str = Field(
        default="20260101",
        description="조회 시작일입니다.",
    )
    end_date: str = Field(
        default="20260107",
        description="조회 종료일입니다.",
    )
    period: PeriodCode = Field(
        default="D",
        description="기간 구분 코드. D(일), W(주), M(월), Y(년) 중 하나입니다.",
    )
    adjusted_price: bool = Field(default=True, description="수정주가 반영 여부입니다.")
    window: int = Field(default=20, ge=1, description="이동평균 계산 기간입니다.")


class MovingAverageResponse(BaseModel):
    """특정 날짜의 가격과 이동평균 값 응답."""

    date: str
    moving_average: float


class RsiRequest(BaseModel):
    """RSI 계산 요청 파라미터."""

    market: str = Field(
        default="J", description="시장 구분 코드. 국내 주식은 J를 사용합니다."
    )
    code: str = Field(
        default="005930", description="종목 코드. 기본값은 삼성전자 005930입니다."
    )
    start_date: str = Field(
        default="20260101",
        description="조회 시작일입니다.",
    )
    end_date: str = Field(
        default="20260107",
        description="조회 종료일입니다.",
    )
    period: PeriodCode = Field(
        default="D",
        description="기간 구분 코드. D(일), W(주), M(월), Y(년) 중 하나입니다.",
    )
    adjusted_price: bool = Field(default=True, description="수정주가 반영 여부입니다.")
    rsi_window: int = Field(default=14, ge=1, description="RSI 계산 기간입니다.")


class RsiResponse(BaseModel):
    """특정 날짜의 RSI 값 응답."""

    date: str
    rsi: float


class RsiSignalRequest(BaseModel):
    """RSI 신호 계산 요청 파라미터."""

    market: str = Field(
        default="J", description="시장 구분 코드. 국내 주식은 J를 사용합니다."
    )
    code: str = Field(
        default="005930", description="종목 코드. 기본값은 삼성전자 005930입니다."
    )
    start_date: str = Field(
        default="20260101",
        description="조회 시작일입니다.",
    )
    end_date: str = Field(
        default="20260107",
        description="조회 종료일입니다.",
    )
    period: PeriodCode = Field(
        default="D",
        description="기간 구분 코드. D(일), W(주), M(월), Y(년) 중 하나입니다.",
    )
    adjusted_price: bool = Field(default=True, description="수정주가 반영 여부입니다.")
    rsi_window: int = Field(default=14, ge=1, description="RSI 계산 기간입니다.")
    ema_window: int = Field(
        default=9, ge=1, description="RSI signal EMA 계산 기간입니다."
    )


class RsiSignalResponse(BaseModel):
    """특정 날짜의 RSI 값과 신호 응답."""

    date: str
    rsi_ema: float
    signal: str


class MacdRequest(BaseModel):
    """MACD 계산 요청 파라미터."""

    market: str = Field(
        default="J", description="시장 구분 코드. 국내 주식은 J를 사용합니다."
    )
    code: str = Field(
        default="005930", description="종목 코드. 기본값은 삼성전자 005930입니다."
    )
    start_date: str = Field(
        default="20260101",
        description="조회 시작일입니다.",
    )
    end_date: str = Field(
        default="20260107",
        description="조회 종료일입니다.",
    )
    period: PeriodCode = Field(
        default="D",
        description="기간 구분 코드. D(일), W(주), M(월), Y(년) 중 하나입니다.",
    )
    adjusted_price: bool = Field(default=True, description="수정주가 반영 여부입니다.")
    ema_short_window: int = Field(
        default=12, ge=1, description="MACD 단기 EMA 계산 기간입니다."
    )
    ema_long_window: int = Field(
        default=26, ge=1, description="MACD 장기 EMA 계산 기간입니다."
    )


class MacdResponse(BaseModel):
    """특정 날짜의 MACD 값과 신호 응답."""

    date: str
    macd: float
