from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TreasuryYieldMaturity(str, Enum):
    """국가와 만기를 함께 식별하는 국채 수익률 조회 구분자."""

    KOREA_1Y = "korea-1y"
    KOREA_3Y = "korea-3y"
    KOREA_5Y = "korea-5y"
    KOREA_10Y = "korea-10y"
    US_1Y = "us-1y"
    US_10Y = "us-10y"


@dataclass
class DomesticMarketIndexPrice:
    """국내 시장 지표 가격 도메인 모델."""

    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    price_diff: float
    price_diff_rate: float
    volume: int
    trading_value: float


@dataclass
class OverseasMarketIndexPrice:
    """해외 시장 지표 가격 도메인 모델."""

    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float


@dataclass
class VKospiIndex:
    """VKOSPI 지수 도메인 모델."""

    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    price_diff: float
    price_diff_rate: float


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
