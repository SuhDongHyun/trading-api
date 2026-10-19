from abc import ABC, abstractmethod
from collections.abc import Sequence

from bitcoin.domain.quotation import (
    Candle,
    DayCandle,
    MinuteCandle,
    Orderbook,
    OrderbookInstrument,
    PeriodCandle,
    Ticker,
    Trade,
    TradingPair,
)


class TradingPairClient(ABC):
    """Upbit 지원 페어 목록 조회 포트."""

    @abstractmethod
    def get_trading_pairs(self, is_details: bool = False) -> list[TradingPair]:
        raise NotImplementedError


class TickerClient(ABC):
    """페어별 현재가 조회 포트."""

    @abstractmethod
    def get_tickers(self, markets: list[str]) -> list[Ticker]:
        raise NotImplementedError


class QuoteTickerClient(ABC):
    """호가 통화별 현재가 조회 포트."""

    @abstractmethod
    def get_tickers(self, quote_currencies: Sequence[str]) -> list[Ticker]:
        raise NotImplementedError


class OrderbookClient(ABC):
    """호가 조회 포트."""

    @abstractmethod
    def get_orderbooks(
        self, markets: list[str], level: str = "0", count: int = 30
    ) -> list[Orderbook]:
        raise NotImplementedError


class OrderbookInstrumentClient(ABC):
    """호가 정책 조회 포트."""

    @abstractmethod
    def get_orderbook_instruments(
        self, markets: list[str]
    ) -> list[OrderbookInstrument]:
        raise NotImplementedError


class TradeClient(ABC):
    """최근 체결 내역 조회 포트."""

    @abstractmethod
    def get_trades(
        self,
        market: str,
        to: str | None = None,
        count: int = 1,
        cursor: str | None = None,
        days_ago: int | None = None,
    ) -> list[Trade]:
        raise NotImplementedError


class CandleClient(ABC):
    """Upbit 캔들 조회 포트."""

    @abstractmethod
    def get_seconds_candles(
        self, market: str, to: str | None = None, count: int = 1
    ) -> list[Candle]:
        raise NotImplementedError

    @abstractmethod
    def get_minute_candles(
        self, unit: int, market: str, to: str | None = None, count: int = 1
    ) -> list[MinuteCandle]:
        raise NotImplementedError

    @abstractmethod
    def get_day_candles(
        self,
        market: str,
        to: str | None = None,
        count: int = 1,
        converting_price_unit: str | None = None,
    ) -> list[DayCandle]:
        raise NotImplementedError

    @abstractmethod
    def get_week_candles(
        self, market: str, to: str | None = None, count: int = 1
    ) -> list[PeriodCandle]:
        raise NotImplementedError

    @abstractmethod
    def get_month_candles(
        self, market: str, to: str | None = None, count: int = 1
    ) -> list[PeriodCandle]:
        raise NotImplementedError

    @abstractmethod
    def get_year_candles(
        self, market: str, to: str | None = None, count: int = 1
    ) -> list[PeriodCandle]:
        raise NotImplementedError
