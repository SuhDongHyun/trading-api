from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import IntEnum
import re
from typing import Literal

from pydantic import Field, field_validator

from stock.interface.schema.common import RequestModel, ResponseModel

MARKET_PATTERN = r"^[A-Z0-9]+-[A-Z0-9]+$"


class TradingPairsRequest(RequestModel):
    """페어 목록 상세 정보 포함 여부."""

    is_details: bool = False


class MarketEventCautionResponse(ResponseModel):
    """시장 주의 사유별 플래그."""

    PRICE_FLUCTUATIONS: bool
    TRADING_VOLUME_SOARING: bool
    DEPOSIT_AMOUNT_SOARING: bool
    GLOBAL_PRICE_DIFFERENCES: bool
    CONCENTRATION_OF_SMALL_ACCOUNTS: bool


class MarketEventResponse(ResponseModel):
    """페어의 시장경보 정보."""

    warning: bool
    caution: MarketEventCautionResponse


class TradingPairResponse(ResponseModel):
    """지원 페어 메타데이터 응답."""

    market: str
    korean_name: str
    english_name: str
    market_warning: str | None = None
    market_event: MarketEventResponse | None = None


class MarketsRequest(RequestModel):
    """하나 이상의 Upbit 페어 코드 목록."""

    markets: list[str] = Field(min_length=1)

    @field_validator("markets")
    @classmethod
    def validate_markets(cls, values: list[str]) -> list[str]:
        if any(not re.fullmatch(MARKET_PATTERN, value) for value in values):
            raise ValueError("각 market은 KRW-BTC 형식의 대문자 페어 코드여야 합니다.")
        return values


class TickerRequest(MarketsRequest):
    """페어 단위 현재가 요청."""


class QuoteTickerRequest(RequestModel):
    """호가 통화 단위 현재가 요청."""

    quote_currencies: list[Literal["KRW", "BTC", "USDT"]] = Field(min_length=1)


class TickerResponse(ResponseModel):
    """Upbit 현재가 스냅샷 응답."""

    market: str
    trade_date: str
    trade_time: str
    trade_date_kst: str
    trade_time_kst: str
    trade_timestamp: int
    opening_price: float
    high_price: float
    low_price: float
    trade_price: float
    prev_closing_price: float
    change: Literal["EVEN", "RISE", "FALL"]
    change_price: float
    change_rate: float
    signed_change_price: float
    signed_change_rate: float
    trade_volume: float
    acc_trade_price: float
    acc_trade_price_24h: float
    acc_trade_volume: float
    acc_trade_volume_24h: float
    highest_52_week_price: float
    highest_52_week_date: str
    lowest_52_week_price: float
    lowest_52_week_date: str
    timestamp: int


class OrderbookRequest(MarketsRequest):
    """호가 요청. level은 Upbit 숫자 문자열 형식이다."""

    level: str = Field(default="0", pattern=r"^(?:0|[1-9]\d*)(?:\.\d+)?$")
    count: int = Field(default=30, ge=1, le=30)

    @field_validator("level")
    @classmethod
    def validate_level(cls, value: str) -> str:
        try:
            level = Decimal(value)
        except InvalidOperation as error:
            raise ValueError("level은 0 이상의 숫자 문자열이어야 합니다.") from error
        if (
            not level.is_finite()
            or level < 0
            or (level >= 1 and ("." in value or level != level.to_integral_value()))
        ):
            raise ValueError("level은 0, 1 이상의 정수 또는 1 미만의 소수여야 합니다.")
        return value


class OrderbookUnitResponse(ResponseModel):
    """매수·매도 한 단계의 가격과 잔량."""

    ask_price: float
    bid_price: float
    ask_size: float
    bid_size: float


class OrderbookResponse(ResponseModel):
    """호가 응답."""

    market: str
    timestamp: int
    total_ask_size: float
    total_bid_size: float
    level: float
    orderbook_units: list[OrderbookUnitResponse]


class OrderbookInstrumentResponse(ResponseModel):
    """호가 정책 응답."""

    market: str
    quote_currency: str
    tick_size: str
    supported_levels: list[str]


class OrderbookInstrumentsRequest(MarketsRequest):
    """호가 정책 조회 요청."""


class TradesRequest(RequestModel):
    """최근 체결 내역 조회 조건."""

    market: str = Field(pattern=MARKET_PATTERN)
    to: str | None = Field(
        default=None,
        pattern=r"^(?:\d{6}|\d{2}:\d{2}:\d{2})$",
        description="UTC 기준 종료 시각(HHmmss 또는 HH:mm:ss)입니다.",
    )
    count: int = Field(default=1, ge=1, le=500)
    cursor: str | None = None
    days_ago: int | None = Field(default=None, ge=1, le=7)

    @field_validator("to")
    @classmethod
    def validate_time(cls, value: str | None) -> str | None:
        if value is None:
            return None
        fmt = "%H:%M:%S" if ":" in value else "%H%M%S"
        try:
            datetime.strptime(value, fmt)
        except ValueError as error:
            raise ValueError(
                "to는 유효한 HHmmss 또는 HH:mm:ss 시각이어야 합니다."
            ) from error
        return value

    @field_validator("cursor")
    @classmethod
    def validate_cursor(cls, value: str | None) -> str | None:
        if value is not None and not re.fullmatch(r"[0-9]+", value):
            raise ValueError("cursor는 sequential_id 숫자 문자열이어야 합니다.")
        return value


class TradeResponse(ResponseModel):
    """최근 체결 내역 한 건."""

    market: str
    trade_date_utc: str
    trade_time_utc: str
    timestamp: int
    trade_price: float
    trade_volume: float
    prev_closing_price: float
    change_price: float
    ask_bid: Literal["ASK", "BID"]
    sequential_id: int


class CandlesRequest(RequestModel):
    """Upbit 캔들 조회 조건."""

    market: str = Field(pattern=MARKET_PATTERN)
    to: str | None = Field(
        default=None,
        description="ISO 8601 형식의 종료 시각입니다.",
    )
    count: int = Field(default=1, ge=1, le=200)

    @field_validator("to")
    @classmethod
    def validate_to(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not re.fullmatch(
            r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$",
            value,
        ):
            raise ValueError("to는 ISO 8601 datetime 형식이어야 합니다.")
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError("to는 유효한 ISO 8601 datetime이어야 합니다.") from error
        return value


class DayCandlesRequest(CandlesRequest):
    """일 캔들 조회와 선택적 원화 종가 환산 조건."""

    converting_price_unit: Literal["KRW"] | None = None


class MinuteCandleUnit(IntEnum):
    """Upbit에서 허용하는 분 캔들 단위."""

    ONE = 1
    THREE = 3
    FIVE = 5
    TEN = 10
    FIFTEEN = 15
    THIRTY = 30
    SIXTY = 60
    TWO_FORTY = 240


class CandleResponse(ResponseModel):
    """초 캔들과 다른 주기의 공통 캔들 필드."""

    market: str
    candle_date_time_utc: str
    candle_date_time_kst: str
    opening_price: float
    high_price: float
    low_price: float
    trade_price: float
    timestamp: int
    candle_acc_trade_price: float
    candle_acc_trade_volume: float


class MinuteCandleResponse(CandleResponse):
    """분 캔들의 조회 단위."""

    unit: int


class DayCandleResponse(CandleResponse):
    """일 캔들의 전일 종가 기준 변동 정보."""

    prev_closing_price: float
    change_price: float
    change_rate: float
    converted_trade_price: float | None = None


class PeriodCandleResponse(CandleResponse):
    """주·월·연 캔들의 집계 기간 시작일."""

    first_day_of_period: str
