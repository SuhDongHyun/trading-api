from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from container import Container
from stock.interface.schema.stock_quote import (
    StockQuoteRequest,
    StockInfoResponse,
    HistoricalStockQuoteRequest,
    DailyStockPriceResponse,
    MovingAverageRequest,
    MovingAverageResponse,
    RsiRequest,
    RsiResponse,
    RsiSignalRequest,
    RsiSignalResponse,
    MacdRequest,
    MacdResponse,
    MacdSignalRequest,
    MacdSignalResponse,
)
from stock.service.stock_quote_service import StockQuoteService

router = APIRouter(prefix="/stock_quote", tags=["stock_quote"])


@router.post("", response_model=StockInfoResponse)
@inject
def get_stock_info(
    request: StockQuoteRequest,
    stock_quote_service: StockQuoteService = Depends(
        Provide[Container.stock_quote_service]
    ),
):
    stock_info = stock_quote_service.get_stock_info(request.market, request.code)
    return StockInfoResponse.model_validate(stock_info)


@router.post("/daily", response_model=list[DailyStockPriceResponse])
@inject
def get_daily_stock_prices(
    request: HistoricalStockQuoteRequest,
    stock_quote_service: StockQuoteService = Depends(
        Provide[Container.stock_quote_service]
    ),
):
    daily_prices = stock_quote_service.get_daily_stock_prices(
        market=request.market,
        code=request.code,
        start_date=request.start_date,
        end_date=request.end_date,
        adjusted_price=request.adjusted_price,
    )
    return [DailyStockPriceResponse.model_validate(price) for price in daily_prices]


@router.post("/daily/moving-average", response_model=list[MovingAverageResponse])
@inject
def get_moving_average(
    request: MovingAverageRequest,
    stock_quote_service: StockQuoteService = Depends(
        Provide[Container.stock_quote_service]
    ),
):
    values = stock_quote_service.get_moving_average(
        market=request.market,
        code=request.code,
        start_date=request.start_date,
        end_date=request.end_date,
        adjusted_price=request.adjusted_price,
        window=request.window,
    )
    return [MovingAverageResponse.model_validate(value) for value in values]


@router.post("/indicator/rsi", response_model=list[RsiResponse])
@inject
def get_rsi(
    request: RsiRequest,
    stock_quote_service: StockQuoteService = Depends(
        Provide[Container.stock_quote_service]
    ),
):
    values = stock_quote_service.get_rsi(
        market=request.market,
        code=request.code,
        start_date=request.start_date,
        end_date=request.end_date,
        adjusted_price=request.adjusted_price,
        rsi_window=request.rsi_window,
    )
    return [RsiResponse.model_validate(value) for value in values]


@router.post("/indicator/rsi-signal", response_model=list[RsiSignalResponse])
@inject
def get_rsi_signal(
    request: RsiSignalRequest,
    stock_quote_service: StockQuoteService = Depends(
        Provide[Container.stock_quote_service]
    ),
):
    values = stock_quote_service.get_rsi_signal(
        market=request.market,
        code=request.code,
        start_date=request.start_date,
        end_date=request.end_date,
        adjusted_price=request.adjusted_price,
        rsi_window=request.rsi_window,
        ema_window=request.ema_window,
    )
    return [RsiSignalResponse.model_validate(value) for value in values]


@router.post("/indicator/macd", response_model=list[MacdResponse])
@inject
def get_macd(
    request: MacdRequest,
    stock_quote_service: StockQuoteService = Depends(
        Provide[Container.stock_quote_service]
    ),
):
    values = stock_quote_service.get_macd(
        market=request.market,
        code=request.code,
        start_date=request.start_date,
        end_date=request.end_date,
        adjusted_price=request.adjusted_price,
        ema_short_window=request.ema_short_window,
        ema_long_window=request.ema_long_window,
    )
    return [MacdResponse.model_validate(value) for value in values]


@router.post("/indicator/macd-signal", response_model=list[MacdSignalResponse])
@inject
def get_macd_signal(
    request: MacdSignalRequest,
    stock_quote_service: StockQuoteService = Depends(
        Provide[Container.stock_quote_service]
    ),
):
    values = stock_quote_service.get_macd_signal(
        market=request.market,
        code=request.code,
        start_date=request.start_date,
        end_date=request.end_date,
        adjusted_price=request.adjusted_price,
        ema_short_window=request.ema_short_window,
        ema_long_window=request.ema_long_window,
        ema_window=request.ema_window,
    )
    return [MacdSignalResponse.model_validate(value) for value in values]
