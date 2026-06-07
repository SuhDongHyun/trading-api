from abc import ABC, abstractmethod


class IApiClient(ABC):
    """서비스 계층이 외부 증권사 API 구현에 의존하지 않도록 하는 포트."""

    @abstractmethod
    def get_account_info(self):
        """계좌 잔고와 보유 종목 요약을 조회한다."""

        raise NotImplementedError

    @abstractmethod
    def get_stock_info(self, market: str, code: str):
        """단일 종목의 현재 시세 정보를 조회한다."""

        raise NotImplementedError

    @abstractmethod
    def get_daily_stock_prices(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        period: str,
        adjusted_price: bool,
    ):
        """지정 기간의 일봉 가격 목록을 조회한다."""

        raise NotImplementedError

    @abstractmethod
    def get_total_news(
        self,
        code: str,
        search_date: str,
        search_time: str,
    ):
        """지정 날짜의 지정 시간까지 발행된 종목 관련 뉴스를 모두 조회한다."""

        raise NotImplementedError

    @abstractmethod
    def get_overseas_market_indicator_prices(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        period: str,
    ):
        """지정 기간의 해외 시장 지표 가격 목록을 조회한다."""

        raise NotImplementedError
