from stock.domain.account import AccountSummary
from stock.domain.port.account_client import AccountClient


class AccountService:
    """계좌 조회 요청을 외부 API 포트로 위임하는 애플리케이션 서비스."""

    def __init__(self, account_client: AccountClient):
        self.account_client = account_client

    def get_account_info(self) -> AccountSummary:
        """외부 API에서 계좌 요약 정보를 조회한다."""

        return self.account_client.get_account_info()
