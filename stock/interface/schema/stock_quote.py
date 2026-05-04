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


class DailyStockPriceSummaryResponse(BaseModel):
    """일봉 결과에 포함되는 종목 식별 요약."""

    name: str
    code: str


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


class DailyStockPriceResultResponse(BaseModel):
    """종목 요약과 일봉 가격 목록 응답."""

    summary: DailyStockPriceSummaryResponse
    prices: list[DailyStockPriceResponse]


class SlowStochasticRequest(BaseModel):
    """Slow Stochastic 계산 요청 파라미터."""

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
    """특정 날짜의 Slow Stochastic 값 응답."""

    date: str
    slow_k: float
    slow_d: float


class SlowStochasticResultResponse(BaseModel):
    """종목 요약과 Slow Stochastic 시계열 응답."""

    summary: DailyStockPriceSummaryResponse
    values: list[SlowStochasticValueResponse]


class RsiRequest(BaseModel):
    """RSI 계산 요청 파라미터."""

    market: str = "J"
    code: str
    start_date: str
    end_date: str
    period: str = "D"
    adjusted_price: bool = True
    rsi_period: int = 14


class RsiValueResponse(BaseModel):
    """특정 날짜의 RSI 값 응답."""

    date: str
    rsi: float


class RsiResultResponse(BaseModel):
    """종목 요약과 RSI 시계열 응답."""

    summary: DailyStockPriceSummaryResponse
    values: list[RsiValueResponse]


class RsiSignalRequest(BaseModel):
    """RSI 신호 계산 요청 파라미터."""

    market: str = "J"
    code: str
    start_date: str
    end_date: str
    period: str = "D"
    adjusted_price: bool = True
    rsi_period: int = 14
    overbought_threshold: float = 70.0
    oversold_threshold: float = 30.0


class RsiSignalValueResponse(BaseModel):
    """특정 날짜의 RSI 값과 신호 응답."""

    date: str
    rsi: float
    signal: str


class RsiSignalResultResponse(BaseModel):
    """종목 요약과 RSI 신호 시계열 응답."""

    summary: DailyStockPriceSummaryResponse
    values: list[RsiSignalValueResponse]


class MovingAverageRequest(BaseModel):
    """이동평균 계산 요청 파라미터."""

    market: str = "J"
    code: str
    start_date: str
    end_date: str
    period: str = "D"
    adjusted_price: bool = True
    window: int = Field(default=20, gt=0)


class MovingAverageValueResponse(BaseModel):
    """특정 날짜의 가격과 이동평균 값 응답."""

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
    """종목 요약과 이동평균 시계열 응답."""

    summary: DailyStockPriceSummaryResponse
    values: list[MovingAverageValueResponse]


class OverboughtOversoldRequest(BaseModel):
    """RSI와 Stochastic 기반 과매수·과매도 신호 요청."""

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
    """특정 날짜의 복합 과매수·과매도 신호 응답."""

    date: str
    rsi: float
    slow_k: float
    slow_d: float
    signal: str


class OverboughtOversoldResultResponse(BaseModel):
    """종목 요약과 복합 과매수·과매도 신호 시계열 응답."""

    summary: DailyStockPriceSummaryResponse
    values: list[OverboughtOversoldValueResponse]
