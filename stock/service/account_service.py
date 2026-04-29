from stock.domain.account import AccountSummary
from stock.domain.adapter.api_client import IApiClient


class AccountService:
    """계좌 조회 요청을 외부 API 포트로 위임하는 애플리케이션 서비스."""

    def __init__(self, api_client: IApiClient):
        self.api_client: IApiClient = api_client

    def get_account_info(self) -> AccountSummary:
        return self.api_client.get_account_info()
