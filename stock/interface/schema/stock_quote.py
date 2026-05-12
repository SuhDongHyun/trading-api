from pydantic import BaseModel, Field


class StockInfoRequest(BaseModel):
    """현재가 조회에 필요한 시장 구분과 종목 코드."""

    market: str
    code: str


class StockInfoResponse(BaseModel):
    """현재가 조회 API 응답 스키마."""

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


class DailyStockPriceRequest(BaseModel):
    """일봉 조회 요청 파라미터."""

    market: str = "J"
    code: str
    start_date: str
    end_date: str
    period: str = "D"
    adjusted_price: bool = True


class DailyStockPriceResponse(BaseModel):
    """특정 거래일의 일봉 가격 응답."""

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


class MovingAverageRequest(BaseModel):
    """이동평균 계산 요청 파라미터."""

    market: str = "J"
    code: str
    start_date: str
    end_date: str
    period: str = "D"
    adjusted_price: bool = True
    window: int = Field(default=20, gt=0)


class MovingAverageResponse(BaseModel):
    """특정 날짜의 가격과 이동평균 값 응답."""

    date: str
    moving_average: float


class RsiRequest(BaseModel):
    """RSI 계산 요청 파라미터."""

    market: str = "J"
    code: str
    start_date: str
    end_date: str
    period: str = "D"
    adjusted_price: bool = True
    rsi_window: int = 14


class RsiResponse(BaseModel):
    """특정 날짜의 RSI 값 응답."""

    date: str
    rsi: float


class RsiSignalRequest(BaseModel):
    """RSI 신호 계산 요청 파라미터."""

    market: str = "J"
    code: str
    start_date: str
    end_date: str
    period: str = "D"
    adjusted_price: bool = True
    rsi_window: int = 14
    ema_window: int = 9


class RsiSignalResponse(BaseModel):
    """특정 날짜의 RSI 값과 신호 응답."""

    date: str
    rsi: float
    signal: str
