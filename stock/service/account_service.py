from stock.domain.account import AccountSummary
from stock.domain.adapter.api_client import IApiClient


class AccountService:
    def __init__(self, api_client: IApiClient):
        self.api_client: IApiClient = api_client

    def get_account_info(self) -> AccountSummary:
        return self.api_client.get_account_info()
