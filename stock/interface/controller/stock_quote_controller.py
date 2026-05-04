from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from container import Container
from stock.interface.schema.stock_quote import (
    DailyStockPriceRequest,
    DailyStockPriceResponse,
    DailyStockPriceResultResponse,
    DailyStockPriceSummaryResponse,
    MovingAverageRequest,
    MovingAverageResultResponse,
    MovingAverageValueResponse,
    OverboughtOversoldRequest,
    OverboughtOversoldResultResponse,
    OverboughtOversoldValueResponse,
    RsiRequest,
    RsiResultResponse,
    RsiSignalRequest,
    RsiSignalResultResponse,
    RsiSignalValueResponse,
    RsiValueResponse,
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
    """현재가 조회 요청을 처리하고 응답 스키마로 변환한다."""

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
    """일봉 조회 요청을 처리하고 날짜별 가격 응답을 만든다."""

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


@router.post("/daily/moving-average", response_model=MovingAverageResultResponse)
@inject
def get_moving_average(
    request: MovingAverageRequest,
    stock_quote_service: StockQuoteService = Depends(
        Provide[Container.stock_quote_service]
    ),
):
    """이동평균 조회 요청을 처리하고 지표 응답을 만든다."""

    moving_average = stock_quote_service.get_moving_average(
        market=request.market,
        code=request.code,
        start_date=request.start_date,
        end_date=request.end_date,
        period=request.period,
        adjusted_price=request.adjusted_price,
        window=request.window,
    )

    return MovingAverageResultResponse(
        summary=DailyStockPriceSummaryResponse(
            name=moving_average.summary.name,
            code=moving_average.summary.code,
        ),
        values=[
            MovingAverageValueResponse(
                date=value.date,
                open_price=value.open_price,
                high_price=value.high_price,
                low_price=value.low_price,
                close_price=value.close_price,
                accumulated_volume=value.accumulated_volume,
                accumulated_trading_value=value.accumulated_trading_value,
                price_diff=value.price_diff,
                price_diff_sign=value.price_diff_sign,
                change_flag=value.change_flag,
                moving_average=value.moving_average,
            )
            for value in moving_average.values
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
    """Slow Stochastic 지표 요청을 처리한다."""

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


@router.post("/indicator/rsi", response_model=RsiResultResponse)
@inject
def get_rsi(
    request: RsiRequest,
    stock_quote_service: StockQuoteService = Depends(
        Provide[Container.stock_quote_service]
    ),
):
    """RSI 지표 요청을 처리한다."""

    indicator = stock_quote_service.get_rsi(
        market=request.market,
        code=request.code,
        start_date=request.start_date,
        end_date=request.end_date,
        period=request.period,
        adjusted_price=request.adjusted_price,
        rsi_period=request.rsi_period,
    )

    return RsiResultResponse(
        summary=DailyStockPriceSummaryResponse(
            name=indicator.summary.name,
            code=indicator.summary.code,
        ),
        values=[
            RsiValueResponse(
                date=value.date,
                rsi=value.rsi,
            )
            for value in indicator.values
        ],
    )


@router.post("/indicator/rsi-signal", response_model=RsiSignalResultResponse)
@inject
def get_rsi_signal(
    request: RsiSignalRequest,
    stock_quote_service: StockQuoteService = Depends(
        Provide[Container.stock_quote_service]
    ),
):
    """RSI 과매수·과매도 신호 요청을 처리한다."""

    signal = stock_quote_service.get_rsi_signal(
        market=request.market,
        code=request.code,
        start_date=request.start_date,
        end_date=request.end_date,
        period=request.period,
        adjusted_price=request.adjusted_price,
        rsi_period=request.rsi_period,
        overbought_threshold=request.overbought_threshold,
        oversold_threshold=request.oversold_threshold,
    )

    return RsiSignalResultResponse(
        summary=DailyStockPriceSummaryResponse(
            name=signal.summary.name,
            code=signal.summary.code,
        ),
        values=[
            RsiSignalValueResponse(
                date=value.date,
                rsi=value.rsi,
                signal=value.signal,
            )
            for value in signal.values
        ],
    )


@router.post(
    "/indicator/overbought-oversold",
    response_model=OverboughtOversoldResultResponse,
)
@inject
def get_overbought_oversold(
    request: OverboughtOversoldRequest,
    stock_quote_service: StockQuoteService = Depends(
        Provide[Container.stock_quote_service]
    ),
):
    """복합 과매수·과매도 신호 요청을 처리한다."""

    signal = stock_quote_service.get_overbought_oversold(
        market=request.market,
        code=request.code,
        start_date=request.start_date,
        end_date=request.end_date,
        period=request.period,
        adjusted_price=request.adjusted_price,
        rsi_period=request.rsi_period,
        stochastic_k_period=request.stochastic_k_period,
        stochastic_k_smoothing_period=request.stochastic_k_smoothing_period,
        stochastic_d_period=request.stochastic_d_period,
        rsi_overbought_threshold=request.rsi_overbought_threshold,
        rsi_oversold_threshold=request.rsi_oversold_threshold,
        stochastic_overbought_threshold=request.stochastic_overbought_threshold,
        stochastic_oversold_threshold=request.stochastic_oversold_threshold,
    )

    return OverboughtOversoldResultResponse(
        summary=DailyStockPriceSummaryResponse(
            name=signal.summary.name,
            code=signal.summary.code,
        ),
        values=[
            OverboughtOversoldValueResponse(
                date=value.date,
                rsi=value.rsi,
                slow_k=value.slow_k,
                slow_d=value.slow_d,
                signal=value.signal,
            )
            for value in signal.values
        ],
    )
