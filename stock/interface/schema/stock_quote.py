from pydantic import BaseModel


class StockInfoRequest(BaseModel):
    market: str
    code: str


class StockInfoResponse(BaseModel):
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
