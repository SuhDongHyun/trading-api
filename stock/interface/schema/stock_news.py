from datetime import datetime
from pydantic import Field, field_validator

from stock.interface.schema.common import RequestModel, ResponseModel, validate_yyyymmdd


class StockNewsRequest(RequestModel):
    """뉴스 조회 요청 파라미터."""

    code: str = Field(
        default="005930", description="종목 코드. 기본값은 삼성전자 005930입니다."
    )
    search_date: str = Field(
        pattern=r"^\d{8}$",
        description="조회 날짜입니다.",
    )
    search_time: str = Field(
        default="",
        description="조회 시간입니다.",
    )

    @field_validator("search_date")
    @classmethod
    def validate_search_date(cls, value: str) -> str:
        return validate_yyyymmdd(value)


class StockNewsResponse(ResponseModel):
    """뉴스 항목 응답 모델."""

    title: str
    source: str
    published_at: datetime
