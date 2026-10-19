from dataclasses import dataclass


@dataclass
class MarketEventCaution:
    """페어의 개별 시장 주의 사유."""

    PRICE_FLUCTUATIONS: bool
    TRADING_VOLUME_SOARING: bool
    DEPOSIT_AMOUNT_SOARING: bool
    GLOBAL_PRICE_DIFFERENCES: bool
    CONCENTRATION_OF_SMALL_ACCOUNTS: bool


@dataclass
class MarketEvent:
    """페어의 거래 유의 및 주의 정보."""

    warning: bool
    caution: MarketEventCaution


@dataclass
class TradingPair:
    """Upbit에서 지원하는 페어 메타데이터."""

    market: str
    korean_name: str
    english_name: str
    market_warning: str | None = None
    market_event: MarketEvent | None = None


@dataclass
class Ticker:
    """페어 현재가 스냅샷."""

    market: str
    trade_date: str
    trade_time: str
    trade_date_kst: str
    trade_time_kst: str
    trade_timestamp: int
    opening_price: float
    high_price: float
    low_price: float
    trade_price: float
    prev_closing_price: float
    change: str
    change_price: float
    change_rate: float
    signed_change_price: float
    signed_change_rate: float
    trade_volume: float
    acc_trade_price: float
    acc_trade_price_24h: float
    acc_trade_volume: float
    acc_trade_volume_24h: float
    highest_52_week_price: float
    highest_52_week_date: str
    lowest_52_week_price: float
    lowest_52_week_date: str
    timestamp: int


@dataclass
class OrderbookUnit:
    """매도·매수 호가 한 단계."""

    ask_price: float
    bid_price: float
    ask_size: float
    bid_size: float


@dataclass
class Orderbook:
    """특정 페어의 현재 호가 스냅샷."""

    market: str
    timestamp: int
    total_ask_size: float
    total_bid_size: float
    level: float
    orderbook_units: list[OrderbookUnit]


@dataclass
class OrderbookInstrument:
    """페어별 호가 단위 정책."""

    market: str
    quote_currency: str
    tick_size: str
    supported_levels: list[str]


@dataclass
class Trade:
    """최근 체결 한 건."""

    market: str
    trade_date_utc: str
    trade_time_utc: str
    timestamp: int
    trade_price: float
    trade_volume: float
    prev_closing_price: float
    change_price: float
    ask_bid: str
    sequential_id: int
