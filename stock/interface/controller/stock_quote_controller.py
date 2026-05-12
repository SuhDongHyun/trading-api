from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from container import Container
from stock.interface.schema.stock_quote import (
    StockInfoRequest,
    StockInfoResponse,
    DailyStockPriceRequest,
    DailyStockPriceResponse,
    MovingAverageRequest,
    MovingAverageResponse,
    RsiRequest,
    RsiResponse,
    RsiSignalRequest,
    RsiSignalResponse,
)
from stock.service.stock_quote_service import StockQuoteService

router = APIRouter(prefix="/stock_quote", tags=["stock_quote"])


@router.post("", response_model=StockInfoResponse)
@inject
def get_stock_info(
    request: StockInfoRequest,
    stock_quote_service: StockQuoteService = Depends(
        Provide[Container.stock_quote_service]
    ),
):
    """현재가 조회 요청을 처리하고 응답 스키마로 변환한다."""

    stock_info = stock_quote_service.get_stock_info(request.market, request.code)

    return StockInfoResponse(
        market_name=stock_info.market_name,
        code=stock_info.code,
        industry=stock_info.industry,
        per=stock_info.per,
        pbr=stock_info.pbr,
        eps=stock_info.eps,
        bps=stock_info.bps,
        open_price=stock_info.open_price,
        current_price=stock_info.current_price,
        previous_price=stock_info.previous_price,
        highest_price=stock_info.highest_price,
        lowest_price=stock_info.lowest_price,
        upper_limit_price=stock_info.upper_limit_price,
        lower_limit_price=stock_info.lower_limit_price,
        current_volume=stock_info.current_volume,
        previous_volume=stock_info.previous_volume,
        current_trading_value=stock_info.current_trading_value,
        price_diff=stock_info.price_diff,
        price_diff_rate=stock_info.price_diff_rate,
    )


@router.post("/daily", response_model=list[DailyStockPriceResponse])
@inject
def get_daily_stock_prices(
    request: DailyStockPriceRequest,
    stock_quote_service: StockQuoteService = Depends(
        Provide[Container.stock_quote_service]
    ),
):
    """일봉 조회 요청을 처리하고 날짜별 가격 응답을 만든다."""

    daily_prices = stock_quote_service.get_daily_stock_prices(
        market=request.market,
        code=request.code,
        start_date=request.start_date,
        end_date=request.end_date,
        period=request.period,
        adjusted_price=request.adjusted_price,
    )

    return [
        DailyStockPriceResponse(
            date=price.date,
            open_price=price.open_price,
            high_price=price.high_price,
            low_price=price.low_price,
            close_price=price.close_price,
            accumulated_volume=price.accumulated_volume,
            accumulated_trading_value=price.accumulated_trading_value,
            price_diff=price.price_diff,
            price_diff_sign=price.price_diff_sign,
            change_flag=price.change_flag,
        )
        for price in daily_prices
    ]


@router.post("/daily/moving-average", response_model=list[MovingAverageResponse])
@inject
def get_moving_average(
    request: MovingAverageRequest,
    stock_quote_service: StockQuoteService = Depends(
        Provide[Container.stock_quote_service]
    ),
):
    """이동평균 조회 요청을 처리하고 지표 응답을 만든다."""

    moving_averages = stock_quote_service.get_moving_average(
        market=request.market,
        code=request.code,
        start_date=request.start_date,
        end_date=request.end_date,
        period=request.period,
        adjusted_price=request.adjusted_price,
        window=request.window,
    )

    return [
        MovingAverageResponse(
            date=moving_average.date,
            moving_average=moving_average.value,
        )
        for moving_average in moving_averages
    ]


@router.post("/indicator/rsi", response_model=list[RsiResponse])
@inject
def get_rsi(
    request: RsiRequest,
    stock_quote_service: StockQuoteService = Depends(
        Provide[Container.stock_quote_service]
    ),
):
    """RSI 지표 요청을 처리한다."""

    rsi_values = stock_quote_service.get_rsi(
        market=request.market,
        code=request.code,
        start_date=request.start_date,
        end_date=request.end_date,
        period=request.period,
        adjusted_price=request.adjusted_price,
        rsi_window=request.rsi_window,
    )

    return [
        RsiResponse(
            date=rsi.date,
            rsi=rsi.value,
        )
        for rsi in rsi_values
    ]


@router.post("/indicator/rsi-signal", response_model=list[RsiSignalResponse])
@inject
def get_rsi_signal(
    request: RsiSignalRequest,
    stock_quote_service: StockQuoteService = Depends(
        Provide[Container.stock_quote_service]
    ),
):
    """RSI 과매수·과매도 신호 요청을 처리한다."""

    rsi_signals = stock_quote_service.get_rsi_signal(
        market=request.market,
        code=request.code,
        start_date=request.start_date,
        end_date=request.end_date,
        period=request.period,
        adjusted_price=request.adjusted_price,
        rsi_window=request.rsi_window,
        ema_window=request.ema_window,
    )

    return [
        RsiSignalResponse(
            date=rsi_signal.date,
            rsi=rsi_signal.value,
            signal=rsi_signal.signal,
        )
        for rsi_signal in rsi_signals
    ]
