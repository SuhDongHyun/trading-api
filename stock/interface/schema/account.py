from pydantic import BaseModel


class PositionResponse(BaseModel):
    code: str
    name: str
    quantity: float
    unrealized_pnl: float
    unrealized_return: float


class AccountResponse(BaseModel):
    cash_balance: float
    total_pnl: float
    total_return: float


class AccountSummaryResponse(BaseModel):
    positions: list[PositionResponse]
    accounts: list[AccountResponse]
