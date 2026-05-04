from dataclasses import dataclass


@dataclass
class StockInfo:
    """단일 종목의 현재가와 거래량 등 시세 상세 정보."""

    market_name: str
    code: str
    industry: str
    per: float
    pbr: float
    eps: float
    bps: float
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
