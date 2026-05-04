from dataclasses import dataclass

from stock.domain.price import DailyStockPriceSummary


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
class RsiSignalValue:
    """특정 날짜의 RSI 값과 단독 신호 판정."""

    date: str
    rsi: float
    signal: str


@dataclass
class RsiSignalResult:
    """종목 요약과 RSI 단독 신호 시계열 결과."""

    summary: DailyStockPriceSummary
    values: list[RsiSignalValue]


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
