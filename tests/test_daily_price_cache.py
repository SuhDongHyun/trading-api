from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Barrier, Event, Lock

import pytest

from stock.domain.stock import DailyStockPrice
from stock.infra.cache.daily_price_cache import (
    DAILY_PRICE_CACHE_TTL_SECONDS,
    MAX_DAILY_PRICE_CACHE_ENTRIES,
    DailyPriceCache,
)


def make_price(date: str) -> DailyStockPrice:
    return DailyStockPrice(
        date=date,
        open_price=1.0,
        high_price=2.0,
        low_price=0.5,
        close_price=1.5,
        accumulated_volume=10,
        accumulated_trading_value=15.0,
        price_diff=0.5,
        price_diff_sign="2",
        change_flag="N",
    )


def date_strings(start: str, end: str) -> list[str]:
    current = datetime.strptime(start, "%Y%m%d").date()
    end_date = datetime.strptime(end, "%Y%m%d").date()
    dates = []
    while current <= end_date:
        dates.append(current.strftime("%Y%m%d"))
        current += timedelta(days=1)
    return dates


class FakeStockQuoteClient:
    def __init__(self, prices: list[DailyStockPrice] | None = None):
        self.prices = prices or [make_price(date) for date in date_strings("20260101", "20260131")]
        self.calls: list[tuple[str, str, str, str, bool]] = []
        self.calls_lock = Lock()
        self.fail_next = False
        self.entered = Event()
        self.release = Event()
        self.block_first_call = False
        self.stock_info = object()

    def get_stock_info(self, market: str, code: str):
        return self.stock_info

    def get_daily_stock_prices(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        adjusted_price: bool,
    ) -> list[DailyStockPrice]:
        with self.calls_lock:
            self.calls.append((market, code, start_date, end_date, adjusted_price))
            call_number = len(self.calls)
            should_fail = self.fail_next
            self.fail_next = False

        if should_fail:
            raise RuntimeError("일봉 조회 실패")
        if self.block_first_call and call_number == 1:
            self.entered.set()
            if not self.release.wait(timeout=3):
                raise TimeoutError("테스트 조회 해제 대기 시간 초과")

        return [
            price
            for price in self.prices
            if start_date <= price.date <= end_date
        ]


class FakeClock:
    def __init__(self, now: float = 100.0):
        self.now = now

    def __call__(self) -> float:
        return self.now


def requested_dates(prices: list[DailyStockPrice]) -> list[str]:
    return [price.date for price in prices]


def test_same_range_reuses_cached_result():
    client = FakeStockQuoteClient()
    cache = DailyPriceCache(client)

    first = cache.get_daily_stock_prices("J", "005930", "20260101", "20260105", True)
    second = cache.get_daily_stock_prices("J", "005930", "20260101", "20260105", True)

    assert len(client.calls) == 1
    assert requested_dates(second) == requested_dates(first)


def test_narrower_range_is_sliced_from_cached_result():
    client = FakeStockQuoteClient()
    cache = DailyPriceCache(client)

    cache.get_daily_stock_prices("J", "005930", "20260101", "20260107", True)
    narrower = cache.get_daily_stock_prices(
        "J", "005930", "20260103", "20260105", True
    )

    assert len(client.calls) == 1
    assert requested_dates(narrower) == ["20260103", "20260104", "20260105"]


def test_extending_range_before_cache_fetches_only_missing_prefix():
    client = FakeStockQuoteClient()
    cache = DailyPriceCache(client)

    cache.get_daily_stock_prices("J", "005930", "20260104", "20260107", True)
    extended = cache.get_daily_stock_prices(
        "J", "005930", "20260101", "20260105", True
    )

    assert client.calls == [
        ("J", "005930", "20260104", "20260107", True),
        ("J", "005930", "20260101", "20260103", True),
    ]
    assert requested_dates(extended) == [
        "20260101",
        "20260102",
        "20260103",
        "20260104",
        "20260105",
    ]


def test_extending_range_after_cache_fetches_only_missing_suffix():
    client = FakeStockQuoteClient()
    cache = DailyPriceCache(client)

    cache.get_daily_stock_prices("J", "005930", "20260104", "20260107", True)
    extended = cache.get_daily_stock_prices(
        "J", "005930", "20260106", "20260110", True
    )

    assert client.calls == [
        ("J", "005930", "20260104", "20260107", True),
        ("J", "005930", "20260108", "20260110", True),
    ]
    assert requested_dates(extended) == [
        "20260106",
        "20260107",
        "20260108",
        "20260109",
        "20260110",
    ]


def test_disjoint_range_replaces_cached_interval():
    client = FakeStockQuoteClient()
    cache = DailyPriceCache(client)

    cache.get_daily_stock_prices("J", "005930", "20260101", "20260103", True)
    later = cache.get_daily_stock_prices(
        "J", "005930", "20260110", "20260112", True
    )
    repeated = cache.get_daily_stock_prices(
        "J", "005930", "20260110", "20260112", True
    )

    assert client.calls == [
        ("J", "005930", "20260101", "20260103", True),
        ("J", "005930", "20260110", "20260112", True),
    ]
    assert requested_dates(later) == requested_dates(repeated)


def test_warmup_across_holiday_and_weekend_preserves_cached_main_range():
    client = FakeStockQuoteClient(
        prices=[
            make_price(date)
            for date in date_strings("20260401", "20260510")
        ]
    )
    cache = DailyPriceCache(client)

    # 2026-05-04의 직전 거래일은 2026-04-30이며, 그 사이는 휴장일과 주말이다.
    main_prices = cache.get_daily_stock_prices(
        "J", "005930", "20260504", "20260508", True
    )
    cache.get_daily_stock_prices("J", "005930", "20260401", "20260430", True)
    repeated_main_prices = cache.get_daily_stock_prices(
        "J", "005930", "20260504", "20260508", True
    )

    assert client.calls == [
        ("J", "005930", "20260504", "20260508", True),
        ("J", "005930", "20260401", "20260503", True),
    ]
    assert requested_dates(repeated_main_prices) == requested_dates(main_prices)


def test_reversed_range_is_delegated_without_caching():
    client = FakeStockQuoteClient()
    cache = DailyPriceCache(client)

    reversed_prices = cache.get_daily_stock_prices(
        "J", "005930", "20260110", "20260105", True
    )
    valid_prices = cache.get_daily_stock_prices(
        "J", "005930", "20260105", "20260110", True
    )

    assert reversed_prices == []
    assert requested_dates(valid_prices) == date_strings("20260105", "20260110")
    assert client.calls == [
        ("J", "005930", "20260110", "20260105", True),
        ("J", "005930", "20260105", "20260110", True),
    ]


def test_expired_entry_is_fetched_again():
    client = FakeStockQuoteClient()
    clock = FakeClock()
    cache = DailyPriceCache(client, clock=clock)

    cache.get_daily_stock_prices("J", "005930", "20260101", "20260103", True)
    clock.now += DAILY_PRICE_CACHE_TTL_SECONDS
    cache.get_daily_stock_prices("J", "005930", "20260101", "20260103", True)

    assert len(client.calls) == 2


def test_extending_entry_keeps_oldest_fetch_time_for_ttl():
    client = FakeStockQuoteClient()
    clock = FakeClock()
    cache = DailyPriceCache(client, clock=clock)

    cache.get_daily_stock_prices("J", "005930", "20260101", "20260103", True)
    clock.now += DAILY_PRICE_CACHE_TTL_SECONDS - 1
    cache.get_daily_stock_prices("J", "005930", "20260101", "20260105", True)
    clock.now += 1
    cache.get_daily_stock_prices("J", "005930", "20260101", "20260105", True)

    assert len(client.calls) == 3
    assert client.calls[-1][2:4] == ("20260101", "20260105")


def test_concurrent_same_key_requests_share_one_fetch():
    client = FakeStockQuoteClient()
    client.block_first_call = True
    cache = DailyPriceCache(client)
    worker_count = 6
    start_barrier = Barrier(worker_count + 1)

    def request_prices():
        start_barrier.wait(timeout=2)
        return cache.get_daily_stock_prices(
            "J", "005930", "20260101", "20260105", True
        )

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = [executor.submit(request_prices) for _ in range(worker_count)]
        start_barrier.wait(timeout=2)
        assert client.entered.wait(timeout=2)
        client.release.set()
        results = [future.result(timeout=3) for future in futures]

    assert len(client.calls) == 1
    assert all(requested_dates(result) == requested_dates(results[0]) for result in results)


def test_market_code_and_adjusted_price_use_independent_entries():
    client = FakeStockQuoteClient()
    cache = DailyPriceCache(client)

    cache.get_daily_stock_prices("J", "005930", "20260101", "20260103", True)
    cache.get_daily_stock_prices("J", "005930", "20260101", "20260103", True)
    cache.get_daily_stock_prices("Q", "005930", "20260101", "20260103", True)
    cache.get_daily_stock_prices("J", "000660", "20260101", "20260103", True)
    cache.get_daily_stock_prices("J", "005930", "20260101", "20260103", False)

    assert len(client.calls) == 4


def test_returned_objects_are_copies_and_cannot_mutate_cache():
    client = FakeStockQuoteClient()
    cache = DailyPriceCache(client)

    first = cache.get_daily_stock_prices("J", "005930", "20260101", "20260103", True)
    first[0].close_price = -100.0
    first[0].date = "19990101"
    second = cache.get_daily_stock_prices(
        "J", "005930", "20260101", "20260103", True
    )

    assert len(client.calls) == 1
    assert second[0].date == "20260101"
    assert second[0].close_price == 1.5
    assert second[0] is not first[0]


def test_internal_error_is_not_cached_and_next_request_retries():
    client = FakeStockQuoteClient()
    client.fail_next = True
    cache = DailyPriceCache(client)

    with pytest.raises(RuntimeError, match="일봉 조회 실패"):
        cache.get_daily_stock_prices("J", "005930", "20260101", "20260103", True)
    prices = cache.get_daily_stock_prices(
        "J", "005930", "20260101", "20260103", True
    )

    assert len(client.calls) == 2
    assert requested_dates(prices) == ["20260101", "20260102", "20260103"]


def test_stock_info_is_delegated_without_caching():
    client = FakeStockQuoteClient()
    cache = DailyPriceCache(client)

    assert cache.get_stock_info("J", "005930") is client.stock_info


def test_cache_evicts_oldest_key_after_reaching_limit():
    client = FakeStockQuoteClient()
    cache = DailyPriceCache(client)

    for index in range(MAX_DAILY_PRICE_CACHE_ENTRIES + 1):
        code = f"{index:06d}"
        cache.get_daily_stock_prices("J", code, "20260101", "20260103", True)

    assert len(cache._entries) == MAX_DAILY_PRICE_CACHE_ENTRIES
    assert ("J", "000000", True) not in cache._entries
