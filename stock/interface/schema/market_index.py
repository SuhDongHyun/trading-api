from datetime import datetime

from pydantic import Field

from stock.interface.schema.common import ResponseModel


class StockMetaInfoResponse(ResponseModel):
    """단일 종목의 기본 정보 응답 모델."""

    market_name: str
    code: str
    name: str
    department: str


class FearAndGreedIndexResponse(ResponseModel):
    """공포탐욕지수 응답 모델."""

    value: float
    condition: str
    updated_at: datetime


class VIXIndexResponse(ResponseModel):
    """VIX 시계열 응답 모델."""

    date: str
    value: float


class VkospiIndexResponse(ResponseModel):
    """VKOSPI 시계열 응답 모델."""

    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    price_diff: float
    price_diff_rate: float


class OverseasMarketIndexResponse(ResponseModel):
    """환율과 해외 시장 지수에 공통으로 쓰는 시계열 응답."""

    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float


class TreasuryYieldResponse(ResponseModel):
    """국채 수익률 응답은 가격 도메인의 종가를 수익률로 노출한다."""

    date: str
    yield_rate: float = Field(validation_alias="close_price")


class DomesticMarketIndexResponse(ResponseModel):
    """KOSPI와 KOSDAQ에 공통으로 쓰는 국내 지수 시계열 응답."""

    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    price_diff: float
    price_diff_rate: float
    volume: int
    trading_value: float
