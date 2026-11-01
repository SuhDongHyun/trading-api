"""국내 종목 일봉 조회 결과를 짧게 공유하는 캐시 래퍼."""

from copy import copy
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta
from _thread import LockType
from threading import Lock
from time import monotonic
from typing import Callable

from common.exchange_calendar import get_krx_calendar
from stock.domain.port.stock_quote_client import StockQuoteClient
from stock.domain.stock import DailyStockPrice, StockInfo

DAILY_PRICE_CACHE_TTL_SECONDS = 10
MAX_DAILY_PRICE_CACHE_ENTRIES = 128


@dataclass(frozen=True)
class _DailyPriceCacheEntry:
    """한 종목의 연속된 날짜 구간과 해당 구간의 조회 시각."""

    start_date: str
    end_date: str
    prices: tuple[DailyStockPrice, ...]
    fetched_at: float


@dataclass
class _KeyLock:
    """요청 중인 종목 키별 잠금과 대기 중인 사용자 수."""

    lock: LockType
    users: int = 0


class DailyPriceCache(StockQuoteClient):
    """종목 일봉을 구간 단위로 캐시하고 동시 요청을 공유한다."""

    def __init__(
        self,
        client: StockQuoteClient,
        clock: Callable[[], float] = monotonic,
    ):
        self._client = client
        self._clock = clock
        self._entries: OrderedDict[
            tuple[str, str, bool], _DailyPriceCacheEntry
        ] = OrderedDict()
        self._entries_lock = Lock()
        self._key_locks: dict[tuple[str, str, bool], _KeyLock] = {}
        self._key_locks_lock = Lock()

    def get_stock_info(self, market: str, code: str) -> StockInfo:
        """현재가 조회는 내부 클라이언트에 그대로 위임한다."""

        return self._client.get_stock_info(market, code)

    def get_daily_stock_prices(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        adjusted_price: bool = True,
    ) -> list[DailyStockPrice]:
        """캐시 구간을 재사용하고 빠진 앞·뒤 날짜만 조회한다."""

        if start_date > end_date:
            return self._client.get_daily_stock_prices(
                market=market,
                code=code,
                start_date=start_date,
                end_date=end_date,
                adjusted_price=adjusted_price,
            )

        key = (market, code, adjusted_price)
        key_lock = self._acquire_key_lock(key)
        try:
            return self._get_prices_for_key(
                key, market, code, start_date, end_date, adjusted_price
            )
        finally:
            self._release_key_lock(key, key_lock)

    def _get_prices_for_key(
        self,
        key: tuple[str, str, bool],
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        adjusted_price: bool,
    ) -> list[DailyStockPrice]:
        now = self._clock()
        with self._entries_lock:
            self._remove_expired_entries(now)
            entry = self._entries.get(key)
            if entry is not None:
                self._entries.move_to_end(key)

        if entry is not None and self._covers(entry, start_date, end_date):
            return self._slice_prices(entry.prices, start_date, end_date)

        if entry is None or self._is_disjoint(entry, start_date, end_date):
            prices = self._fetch_prices(
                market, code, start_date, end_date, adjusted_price
            )
            updated = _DailyPriceCacheEntry(
                start_date=start_date,
                end_date=end_date,
                prices=tuple(prices),
                fetched_at=now,
            )
        else:
            fetched_prices: list[DailyStockPrice] = []
            expanded_start = min(start_date, entry.start_date)
            expanded_end = max(end_date, entry.end_date)

            if start_date < entry.start_date:
                missing_end = self._previous_day(entry.start_date)
                fetched_prices.extend(
                    self._fetch_prices(
                        market, code, start_date, missing_end, adjusted_price
                    )
                )
            if end_date > entry.end_date:
                missing_start = self._next_day(entry.end_date)
                fetched_prices.extend(
                    self._fetch_prices(
                        market, code, missing_start, end_date, adjusted_price
                    )
                )

            merged_prices = self._merge_prices(entry.prices, fetched_prices)
            updated = _DailyPriceCacheEntry(
                start_date=expanded_start,
                end_date=expanded_end,
                prices=tuple(merged_prices),
                fetched_at=min(entry.fetched_at, now),
            )

        with self._entries_lock:
            self._entries[key] = updated
            self._entries.move_to_end(key)
            self._evict_oldest_entries()

        return self._slice_prices(updated.prices, start_date, end_date)

    def _fetch_prices(
        self,
        market: str,
        code: str,
        start_date: str,
        end_date: str,
        adjusted_price: bool,
    ) -> list[DailyStockPrice]:
        prices = self._client.get_daily_stock_prices(
            market=market,
            code=code,
            start_date=start_date,
            end_date=end_date,
            adjusted_price=adjusted_price,
        )
        return self._slice_prices(prices, start_date, end_date)

    @staticmethod
    def _covers(entry: _DailyPriceCacheEntry, start_date: str, end_date: str):
        return entry.start_date <= start_date and end_date <= entry.end_date

    def _is_disjoint(
        self, entry: _DailyPriceCacheEntry, start_date: str, end_date: str
    ) -> bool:
        if end_date < entry.start_date:
            gap_start = self._next_day(end_date)
            gap_end = self._previous_day(entry.start_date)
        elif start_date > entry.end_date:
            gap_start = self._next_day(entry.end_date)
            gap_end = self._previous_day(start_date)
        else:
            return False

        if gap_start > gap_end:
            return False
        sessions = get_krx_calendar().sessions_in_range(gap_start, gap_end)
        return len(sessions) > 0

    @staticmethod
    def _previous_day(date_string: str) -> str:
        date = datetime.strptime(date_string, "%Y%m%d").date() - timedelta(days=1)
        return date.strftime("%Y%m%d")

    @staticmethod
    def _next_day(date_string: str) -> str:
        date = datetime.strptime(date_string, "%Y%m%d").date() + timedelta(days=1)
        return date.strftime("%Y%m%d")

    @staticmethod
    def _merge_prices(
        existing: tuple[DailyStockPrice, ...],
        additions: list[DailyStockPrice],
    ) -> list[DailyStockPrice]:
        prices_by_date = {price.date: copy(price) for price in existing}
        for price in additions:
            prices_by_date.setdefault(price.date, copy(price))
        return [prices_by_date[date] for date in sorted(prices_by_date)]

    @staticmethod
    def _slice_prices(
        prices: tuple[DailyStockPrice, ...] | list[DailyStockPrice],
        start_date: str,
        end_date: str,
    ) -> list[DailyStockPrice]:
        return [
            copy(price)
            for price in prices
            if start_date <= price.date <= end_date
        ]

    def _remove_expired_entries(self, now: float) -> None:
        expired_keys = [
            key
            for key, entry in self._entries.items()
            if now - entry.fetched_at >= DAILY_PRICE_CACHE_TTL_SECONDS
        ]
        for key in expired_keys:
            del self._entries[key]

    def _evict_oldest_entries(self) -> None:
        while len(self._entries) > MAX_DAILY_PRICE_CACHE_ENTRIES:
            self._entries.popitem(last=False)

    def _acquire_key_lock(self, key: tuple[str, str, bool]) -> _KeyLock:
        with self._key_locks_lock:
            key_lock = self._key_locks.get(key)
            if key_lock is None:
                key_lock = _KeyLock(lock=Lock())
                self._key_locks[key] = key_lock
            key_lock.users += 1
        key_lock.lock.acquire()
        return key_lock

    def _release_key_lock(self, key: tuple[str, str, bool], key_lock: _KeyLock):
        key_lock.lock.release()
        with self._key_locks_lock:
            key_lock.users -= 1
            if key_lock.users == 0 and self._key_locks.get(key) is key_lock:
                del self._key_locks[key]
