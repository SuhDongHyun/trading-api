from datetime import datetime
from pydantic import BaseModel, Field


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
