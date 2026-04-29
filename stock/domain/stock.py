from dataclasses import dataclass


@dataclass
class Stock:
    market_name: str
    code: str
    industry: str
    open_price: float
    current_price: float
    previous_price: float
    highest_price: float
    lowest_price: float
    upper_limit_price: float
    lower_limit_price: float
    current_volume: int
    previous_volume: int
    current_trading_value: float
    price_diff: float
    price_diff_rate: float


@dataclass
class DailyStockPriceSummary:
    name: str
    code: str


@dataclass
class DailyStockPrice:
    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    accumulated_volume: int
    accumulated_trading_value: float
    price_diff: float
    price_diff_sign: str
    change_flag: str


@dataclass
class DailyStockPriceResult:
    summary: DailyStockPriceSummary
    prices: list[DailyStockPrice]


@dataclass
class SlowStochasticValue:
    date: str
    slow_k: float
    slow_d: float


@dataclass
class SlowStochasticResult:
    summary: DailyStockPriceSummary
    values: list[SlowStochasticValue]


@dataclass
class RsiValue:
    date: str
    rsi: float


@dataclass
class RsiResult:
    summary: DailyStockPriceSummary
    values: list[RsiValue]


@dataclass
class MovingAverageValue:
    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    accumulated_volume: int
    accumulated_trading_value: float
    price_diff: float
    price_diff_sign: str
    change_flag: str
    moving_average: float | None


@dataclass
class MovingAverageResult:
    summary: DailyStockPriceSummary
    values: list[MovingAverageValue]


@dataclass
class OverboughtOversoldValue:
    date: str
    rsi: float
    slow_k: float
    slow_d: float
    signal: str


@dataclass
class OverboughtOversoldResult:
    summary: DailyStockPriceSummary
    values: list[OverboughtOversoldValue]
