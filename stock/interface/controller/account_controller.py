from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from container import Container
from stock.service.account_service import AccountService
from stock.interface.schema.account import AccountSummaryResponse

router = APIRouter(prefix="/account", tags=["account"])


@router.get("", response_model=AccountSummaryResponse)
@inject
def get_account_summary(
    account_service: AccountService = Depends(Provide[Container.account_service]),
):
    account_summary = account_service.get_account_info()
    return AccountSummaryResponse.model_validate(account_summary)
