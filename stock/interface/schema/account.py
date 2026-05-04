from pydantic import BaseModel


class PositionResponse(BaseModel):
    """보유 종목 한 건의 API 응답 스키마."""

    code: str
    name: str
    quantity: float
    unrealized_pnl: float
    unrealized_return: float


class AccountResponse(BaseModel):
    """계좌 현금과 평가 손익의 API 응답 스키마."""

    cash_balance: float
    total_pnl: float
    total_return: float


class AccountSummaryResponse(BaseModel):
    """보유 종목 목록과 계좌 요약을 묶은 API 응답 스키마."""

    positions: list[PositionResponse]
    accounts: list[AccountResponse]
