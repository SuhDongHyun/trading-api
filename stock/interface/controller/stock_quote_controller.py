from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from container import Container
from stock.interface.schema.stock_quote import (
    DailyStockPriceRequest,
    DailyStockPriceResponse,
    DailyStockPriceResultResponse,
    DailyStockPriceSummaryResponse,
    SlowStochasticRequest,
    SlowStochasticResultResponse,
    SlowStochasticValueResponse,
    StockInfoRequest,
    StockInfoResponse,
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
    stock_info = stock_quote_service.get_stock_info(request.market, request.code)

    return StockInfoResponse(
        market_name=stock_info.market_name,
        code=stock_info.code,
        industry=stock_info.industry,
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


@router.post("/daily", response_model=DailyStockPriceResultResponse)
@inject
def get_daily_stock_prices(
    request: DailyStockPriceRequest,
    stock_quote_service: StockQuoteService = Depends(
        Provide[Container.stock_quote_service]
    ),
):
    daily_prices = stock_quote_service.get_daily_stock_prices(
        market=request.market,
        code=request.code,
        start_date=request.start_date,
        end_date=request.end_date,
        period=request.period,
        adjusted_price=request.adjusted_price,
    )

    return DailyStockPriceResultResponse(
        summary=DailyStockPriceSummaryResponse(
            name=daily_prices.summary.name,
            code=daily_prices.summary.code,
        ),
        prices=[
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
            for price in daily_prices.prices
        ],
    )


@router.post("/indicator/slow-stochastic", response_model=SlowStochasticResultResponse)
@inject
def get_slow_stochastic(
    request: SlowStochasticRequest,
    stock_quote_service: StockQuoteService = Depends(
        Provide[Container.stock_quote_service]
    ),
):
    indicator = stock_quote_service.get_slow_stochastic(
        market=request.market,
        code=request.code,
        start_date=request.start_date,
        end_date=request.end_date,
        period=request.period,
        adjusted_price=request.adjusted_price,
        k_period=request.k_period,
        k_smoothing_period=request.k_smoothing_period,
        d_period=request.d_period,
    )

    return SlowStochasticResultResponse(
        summary=DailyStockPriceSummaryResponse(
            name=indicator.summary.name,
            code=indicator.summary.code,
        ),
        values=[
            SlowStochasticValueResponse(
                date=value.date,
                slow_k=value.slow_k,
                slow_d=value.slow_d,
            )
            for value in indicator.values
        ],
    )
