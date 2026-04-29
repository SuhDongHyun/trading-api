from dataclasses import dataclass


@dataclass
class Position:
    """계좌가 보유한 단일 종목의 수량과 평가 손익."""

    code: str
    name: str
    quantity: float
    unrealized_pnl: float
    unrealized_return: float


@dataclass
class Account:
    """현금 잔고와 계좌 전체 평가 손익 요약."""

    cash_balance: float
    total_pnl: float
    total_return: float


@dataclass
class AccountSummary:
    """잔고 종목 목록과 계좌 평가 정보를 함께 반환하는 도메인 결과."""

    positions: list[Position]
    accounts: list[Account]
