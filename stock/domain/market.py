from dataclasses import dataclass
from datetime import datetime


@dataclass
class FearAndGreedIndex:
    """공포와 탐욕 지수 도메인 모델."""

    value: float
    condition: str
    updated_at: datetime


@dataclass
class VIXIndex:
    """VIX 지수 도메인 모델."""

    date: str
    value: float


@dataclass
class MarketIndicatorPrice:
    """시장 지표 가격 도메인 모델."""

    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
