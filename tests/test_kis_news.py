from datetime import datetime, timedelta

from stock.infra.kis.kis_client import KISClient


class FakeNewsClient(KISClient):
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def _get_news(self, code: str, search_date: str, search_time: str) -> list[dict]:
        self.calls.append((code, search_date, search_time))
        return self.pages[len(self.calls) - 1]


def make_news(key: str, published_at: datetime, code: str = "005930") -> dict:
    return {
        "cntt_usiq_srno": key,
        "hts_pbnt_titl_cntt": f"title-{key}",
        "dorg": "source",
        "data_dt": published_at.strftime("%Y%m%d"),
        "data_tm": published_at.strftime("%H%M%S"),
        "iscd1": code,
        "iscd2": "",
        "iscd3": "",
        "iscd4": "",
        "iscd5": "",
    }


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


def test_get_total_news_stops_after_crossing_initial_search_date():
    first_page = [
        make_news(
            str(index),
            datetime(2026, 5, 31, 18, 0, 0) - timedelta(minutes=index),
            code="000660",
        )
        for index in range(40)
    ]
    second_page = [
        first_page[-1],
        *[
            make_news(
                str(index),
                datetime(2026, 5, 29, 18, 0, 0) - timedelta(minutes=index),
                code="000660",
            )
            for index in range(40, 79)
        ],
    ]
    client = FakeNewsClient([first_page, second_page, []])

    result = client.get_total_news("000660", "20260531", "")

    assert client.calls == [
        ("000660", "20260531", ""),
        ("000660", "20260531", "172100"),
    ]
    assert [news.key for news in result] == [str(index) for index in range(40)]
