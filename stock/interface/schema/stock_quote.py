from pydantic import BaseModel, Field


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


class DailyStockPriceRequest(BaseModel):
    market: str = "J"
    code: str
    start_date: str
    end_date: str
    period: str = "D"
    adjusted_price: bool = True


class DailyStockPriceSummaryResponse(BaseModel):
    name: str
    code: str


class DailyStockPriceResponse(BaseModel):
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


class DailyStockPriceResultResponse(BaseModel):
    summary: DailyStockPriceSummaryResponse
    prices: list[DailyStockPriceResponse]


class SlowStochasticRequest(BaseModel):
    market: str = "J"
    code: str
    start_date: str
    end_date: str
    period: str = "D"
    adjusted_price: bool = True
    k_period: int = 14
    k_smoothing_period: int = 3
    d_period: int = 3


class SlowStochasticValueResponse(BaseModel):
    date: str
    slow_k: float
    slow_d: float


class SlowStochasticResultResponse(BaseModel):
    summary: DailyStockPriceSummaryResponse
    values: list[SlowStochasticValueResponse]


class RsiRequest(BaseModel):
    market: str = "J"
    code: str
    start_date: str
    end_date: str
    period: str = "D"
    adjusted_price: bool = True
    rsi_period: int = 14


class RsiValueResponse(BaseModel):
    date: str
    rsi: float


class RsiResultResponse(BaseModel):
    summary: DailyStockPriceSummaryResponse
    values: list[RsiValueResponse]


class MovingAverageRequest(BaseModel):
    market: str = "J"
    code: str
    start_date: str
    end_date: str
    period: str = "D"
    adjusted_price: bool = True
    window: int = Field(default=20, gt=0)


class MovingAverageValueResponse(BaseModel):
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


class MovingAverageResultResponse(BaseModel):
    summary: DailyStockPriceSummaryResponse
    values: list[MovingAverageValueResponse]


class OverboughtOversoldRequest(BaseModel):
    market: str = "J"
    code: str
    start_date: str
    end_date: str
    period: str = "D"
    adjusted_price: bool = True
    rsi_period: int = 14
    stochastic_k_period: int = 14
    stochastic_k_smoothing_period: int = 3
    stochastic_d_period: int = 3
    rsi_overbought_threshold: float = 70.0
    rsi_oversold_threshold: float = 30.0
    stochastic_overbought_threshold: float = 80.0
    stochastic_oversold_threshold: float = 20.0


class OverboughtOversoldValueResponse(BaseModel):
    date: str
    rsi: float
    slow_k: float
    slow_d: float
    signal: str


class OverboughtOversoldResultResponse(BaseModel):
    summary: DailyStockPriceSummaryResponse
    values: list[OverboughtOversoldValueResponse]
