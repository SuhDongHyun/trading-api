from dataclasses import dataclass


@dataclass
class Position:
    code: str
    name: str
    quantity: float
    unrealized_pnl: float
    unrealized_return: float


@dataclass
class Account:
    cash_balance: float
    total_pnl: float
    total_return: float


@dataclass
class AccountSummary:
    positions: list[Position]
    accounts: list[Account]
