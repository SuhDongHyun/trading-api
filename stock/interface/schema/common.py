"""HTTP 요청과 응답에서 공유하는 Pydantic 모델."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class RequestModel(BaseModel):
    """요청에 정의되지 않은 필드가 들어오면 거부한다."""

    model_config = ConfigDict(extra="forbid")


class ResponseModel(BaseModel):
    """도메인 dataclass의 속성에서 응답 필드를 읽는다."""

    model_config = ConfigDict(from_attributes=True)


def validate_yyyymmdd(value: str) -> str:
    """스키마 단계에서 실제 달력 날짜인지 확인해 외부 호출의 날짜 오류를 막는다."""

    try:
        datetime.strptime(value, "%Y%m%d")
    except ValueError as error:
        raise ValueError("실제 존재하는 YYYYMMDD 날짜여야 합니다.") from error
    return value


class DateRangeRequest(RequestModel):
    """시작일과 종료일을 함께 받는 조회 요청."""

    start_date: str = Field(
        pattern=r"^\d{8}$",
        description="조회 시작일입니다.",
    )
    end_date: str = Field(
        pattern=r"^\d{8}$",
        description="조회 종료일입니다.",
    )

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_calendar_date(cls, value: str) -> str:
        return validate_yyyymmdd(value)

    @model_validator(mode="after")
    def validate_date_range(self):
        """YYYYMMDD는 문자열 비교와 날짜 비교가 같으므로 시작일 ≤ 종료일만 확인한다."""

        if self.start_date > self.end_date:
            raise ValueError("start_date는 end_date보다 늦을 수 없습니다.")
        return self
