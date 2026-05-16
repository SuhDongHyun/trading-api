from dataclasses import dataclass


@dataclass
class MovingAverage:
    """일별 가격 정보에 이동평균 값을 덧붙인 결과."""

    date: str
    value: float


@dataclass
class Rsi:
    """특정 날짜의 RSI 지표 값."""

    date: str
    value: float


@dataclass
class RsiSignal:
    """특정 날짜의 RSI 값과 단독 신호 판정."""

    date: str
    value: float
    signal: str


@dataclass
class Macd:
    """특정 날짜의 MACD 지표 값."""

    date: str
    value: float


@dataclass
class MacdSignal:
    """특정 날짜의 MACD 값과 단독 신호 판정."""

    date: str
    value: float
    signal: str
