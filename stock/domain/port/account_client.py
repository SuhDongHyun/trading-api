from abc import ABC, abstractmethod

from stock.domain.account import AccountSummary


class AccountClient(ABC):
    """계좌 조회 결과를 제공하는 포트."""

    @abstractmethod
    def get_account_info(self) -> AccountSummary:
        """계좌 잔고와 보유 종목 요약을 조회한다."""

        raise NotImplementedError
