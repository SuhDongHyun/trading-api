from datetime import datetime, timedelta

from stock.domain.news import News
from stock.infra.kis.kis_client import KISClient


class FakeNewsClient(KISClient):
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def _get_news(self, code: str, search_date: str, search_time: str) -> list[News]:
        self.calls.append((code, search_date, search_time))
        return self.pages[len(self.calls) - 1]


def make_news(key: str, published_at: datetime) -> News:
    return News(
        key=key,
        title=f"title-{key}",
        source="source",
        published_at=published_at,
    )


def test_get_total_news_fetches_until_page_has_less_than_forty_and_deduplicates():
    base_time = datetime(2026, 5, 27, 9, 0, 0)
    first_page = [
        make_news(str(index), base_time - timedelta(minutes=index))
        for index in range(40)
    ]
    second_page = [
        first_page[-1],
        make_news("40", datetime(2026, 5, 27, 8, 19, 0)),
        make_news("41", datetime(2026, 5, 27, 8, 18, 0)),
    ]
    client = FakeNewsClient([first_page, second_page])

    result = client.get_total_news("005930", "20260527", "090000")

    assert client.calls == [
        ("005930", "20260527", "090000"),
        ("005930", "20260527", "082100"),
    ]
    assert [news.key for news in result] == [str(index) for index in range(42)]


def test_get_total_news_returns_only_news_from_initial_search_date():
    base_time = datetime(2026, 5, 27, 0, 39, 0)
    first_page = [
        make_news(str(index), base_time - timedelta(minutes=index))
        for index in range(40)
    ]
    second_page = [
        first_page[-1],
        make_news("40", datetime(2026, 5, 26, 23, 59, 0)),
        make_news("41", datetime(2026, 5, 26, 23, 58, 0)),
    ]
    client = FakeNewsClient([first_page, second_page])

    result = client.get_total_news("005930", "20260527", "004000")

    assert [news.key for news in result] == [str(index) for index in range(40)]
