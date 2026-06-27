from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class DateRangeRequest(BaseModel):
    """조회 날짜 범위 요청 모델."""

    start_date: str = Field(
        default="20260101",
        pattern=r"^\d{8}$",
        description="조회 시작일입니다.",
    )
    end_date: str = Field(
        default="20260107",
        pattern=r"^\d{8}$",
        description="조회 종료일입니다.",
    )

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.start_date > self.end_date:
            raise ValueError("start_date는 end_date보다 늦을 수 없습니다.")
        return self


class FearAndGreedIndexResponse(BaseModel):
    """공포탐욕지수 응답 모델."""

    value: float
    condition: str
    updated_at: datetime


class VIXIndexRequest(DateRangeRequest):
    """VIX 지수 조회 요청 모델."""

    pass


class VIXIndexResponse(BaseModel):
    """VIX 지수 응답 모델."""

    date: str
    value: float


class VkospiIndexRequest(DateRangeRequest):
    """VKOSPI 지수 조회 요청 모델."""

    pass


class VkospiIndexResponse(BaseModel):
    """VKOSPI 지수 응답 모델."""

    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    price_diff: float
    price_diff_rate: float


class UsdKrwExchangeRateRequest(DateRangeRequest):
    """USD/KRW 환율 조회 요청 모델."""

    pass


class UsdKrwExchangeRateResponse(BaseModel):
    """USD/KRW 환율 응답 모델."""

    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float


class TreasuryYieldRequest(DateRangeRequest):
    """국채 수익률 조회 요청 모델."""

    pass


class TreasuryYieldResponse(BaseModel):
    """국채 수익률 응답 모델."""

    date: str
    yield_rate: float


class SP500IndexRequest(DateRangeRequest):
    """S&P 500 지수 조회 요청 모델."""

    pass


class SP500IndexResponse(BaseModel):
    """S&P 500 지수 응답 모델."""

    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float


class KospiIndexRequest(DateRangeRequest):
    """KOSPI 지수 조회 요청 모델."""

    pass


class KospiIndexResponse(BaseModel):
    """KOSPI 지수 응답 모델."""

    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    price_diff: float
    price_diff_rate: float
    volume: int
    trading_value: float


class KosdaqIndexRequest(DateRangeRequest):
    """KOSDAQ 지수 조회 요청 모델."""

    pass


class KosdaqIndexResponse(BaseModel):
    """KOSDAQ 지수 응답 모델."""

    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    price_diff: float
    price_diff_rate: float
    volume: int
    trading_value: float
