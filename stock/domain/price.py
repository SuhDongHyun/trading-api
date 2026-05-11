from dataclasses import dataclass


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
