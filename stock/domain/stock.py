from dataclasses import dataclass


@dataclass
class Stock:
    """단일 종목의 현재가와 거래량 등 시세 상세 정보."""

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
    """일봉 조회 결과에 공통으로 붙는 종목 식별 정보."""

    name: str
    code: str


@dataclass
class DailyStockPrice:
    """특정 거래일의 OHLC 가격과 거래대금 정보."""

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
    """일봉 요약 정보와 날짜별 가격 목록."""

    summary: DailyStockPriceSummary
    prices: list[DailyStockPrice]


@dataclass
class SlowStochasticValue:
    """특정 날짜의 Slow Stochastic K/D 지표 값."""

    date: str
    slow_k: float
    slow_d: float


@dataclass
class SlowStochasticResult:
    """종목 요약과 Slow Stochastic 시계열 결과."""

    summary: DailyStockPriceSummary
    values: list[SlowStochasticValue]


@dataclass
class RsiValue:
    """특정 날짜의 RSI 지표 값."""

    date: str
    rsi: float


@dataclass
class RsiResult:
    """종목 요약과 RSI 시계열 결과."""

    summary: DailyStockPriceSummary
    values: list[RsiValue]


@dataclass
class MovingAverageValue:
    """일별 가격 정보에 이동평균 값을 덧붙인 결과."""

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
    """종목 요약과 이동평균 시계열 결과."""

    summary: DailyStockPriceSummary
    values: list[MovingAverageValue]


@dataclass
class OverboughtOversoldValue:
    """RSI와 Slow Stochastic을 조합한 과매수/과매도 판정."""

    date: str
    rsi: float
    slow_k: float
    slow_d: float
    signal: str


@dataclass
class OverboughtOversoldResult:
    """종목 요약과 과매수/과매도 판정 시계열 결과."""

    summary: DailyStockPriceSummary
    values: list[OverboughtOversoldValue]
