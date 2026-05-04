from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from container import Container
from stock.service.account_service import AccountService
from stock.interface.schema.account import (
    PositionResponse,
    AccountResponse,
    AccountSummaryResponse,
)

router = APIRouter(prefix="/account", tags=["account"])


@router.get("", response_model=AccountSummaryResponse)
@inject
def get_account_summary(
    account_service: AccountService = Depends(Provide[Container.account_service]),
):
    """계좌 요약 도메인 결과를 API 응답 스키마로 변환한다."""

    account_summary = account_service.get_account_info()

    return AccountSummaryResponse(
        positions=[
            PositionResponse(
                code=position.code,
                name=position.name,
                quantity=position.quantity,
                unrealized_pnl=position.unrealized_pnl,
                unrealized_return=position.unrealized_return,
            )
            for position in account_summary.positions
        ],
        accounts=[
            AccountResponse(
                cash_balance=account.cash_balance,
                total_pnl=account.total_pnl,
                total_return=account.total_return,
            )
            for account in account_summary.accounts
        ],
    )
