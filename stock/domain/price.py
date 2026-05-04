from dataclasses import dataclass


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
