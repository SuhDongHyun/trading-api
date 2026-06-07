from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field

PeriodCode = Literal["D", "W", "M", "Y"]


class FearAndGreedIndexResponse(BaseModel):
    """공포탐욕지수 응답 모델."""

    value: float
    condition: str
    updated_at: datetime


class VIXIndexRequest(BaseModel):
    """VIX 지수 조회 요청 모델."""

    start_date: str = Field(
        default="20260101",
        description="조회 시작일입니다.",
    )
    end_date: str = Field(
        default="20260107",
        description="조회 종료일입니다.",
    )


class VIXIndexResponse(BaseModel):
    """VIX 지수 응답 모델."""

    date: str
    value: float


class UsdKrwExchangeRateRequest(BaseModel):
    """USD/KRW 환율 조회 요청 모델."""

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


class UsdKrwExchangeRateResponse(BaseModel):
    """USD/KRW 환율 응답 모델."""

    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float


class TreasuryYieldRequest(BaseModel):
    """국채 수익률 조회 요청 모델."""

    start_date: str = Field(
        default="20260101",
        description="조회 시작일입니다.",
    )
    end_date: str = Field(
        default="20260107",
        description="조회 종료일입니다.",
    )


class TreasuryYieldResponse(BaseModel):
    """국채 수익률 응답 모델."""

    date: str
    yield_rate: float
