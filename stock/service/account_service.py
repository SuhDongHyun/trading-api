from stock.domain.account import AccountSummary
from stock.domain.adapter.api_client import IApiClient


class AccountService:
    """계좌 조회 요청을 외부 API 포트로 위임하는 애플리케이션 서비스."""

    def __init__(self, api_client: IApiClient):
        """계좌 정보를 조회할 API 클라이언트를 주입받는다."""

        self.api_client: IApiClient = api_client

    def get_account_info(self) -> AccountSummary:
        """외부 API에서 계좌 요약 정보를 조회한다."""

        return self.api_client.get_account_info()
