from abc import ABC, abstractmethod

from stock.domain.news import News


class NewsClient(ABC):
    """종목 관련 뉴스를 제공하는 포트."""

    @abstractmethod
    def get_total_news(
        self, code: str, search_date: str, search_time: str
    ) -> list[News]:
        """지정 날짜와 시각까지 발행된 종목 뉴스를 조회한다."""

        raise NotImplementedError
