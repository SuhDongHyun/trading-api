from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from container import Container
from stock.service.market_indicator_service import MarketIndicatorService
from stock.interface.schema.market_indicator import (
    FearAndGreedIndexResponse,
    VIXIndexRequest,
    VIXIndexResponse,
    UsdKrwExchangeRateRequest,
    UsdKrwExchangeRateResponse,
    TreasuryYieldRequest,
    TreasuryYieldResponse,
)

router = APIRouter(prefix="/market-indicator", tags=["market-indicator"])


@router.get("/fear-and-greed-index", response_model=FearAndGreedIndexResponse)
@inject
def get_fear_and_greed_index(
    market_indicator_service: MarketIndicatorService = Depends(
        Provide[Container.market_indicator_service]
    ),
):
    """공포탐욕지수 조회 요청을 처리한다."""

    fear_and_greed_index = market_indicator_service.get_fear_and_greed_index()

    return FearAndGreedIndexResponse(
        value=fear_and_greed_index.value,
        condition=fear_and_greed_index.condition,
        updated_at=fear_and_greed_index.updated_at,
    )


@router.post("/vix-index", response_model=list[VIXIndexResponse])
@inject
def get_vix_index(
    request: VIXIndexRequest,
    market_indicator_service: MarketIndicatorService = Depends(
        Provide[Container.market_indicator_service]
    ),
):
    """VIX 지수 조회 요청을 처리한다."""

    vix_index_list = market_indicator_service.get_vix_index(
        start_date=request.start_date, end_date=request.end_date
    )

    return [
        VIXIndexResponse(
            date=vix_index.date,
            value=vix_index.value,
        )
        for vix_index in vix_index_list
    ]


@router.post("/usd-krw-exchange-rate", response_model=list[UsdKrwExchangeRateResponse])
@inject
def get_usd_krw_exchange_rate(
    request: UsdKrwExchangeRateRequest,
    market_indicator_service: MarketIndicatorService = Depends(
        Provide[Container.market_indicator_service]
    ),
):
    """USD/KRW 환율 조회 요청을 처리한다."""

    usd_krw_exchange_rate_list = market_indicator_service.get_usd_krw_exchange_rate(
        start_date=request.start_date, end_date=request.end_date, period=request.period
    )

    return [
        UsdKrwExchangeRateResponse(
            date=exchange_rate.date,
            open_price=exchange_rate.open_price,
            high_price=exchange_rate.high_price,
            low_price=exchange_rate.low_price,
            close_price=exchange_rate.close_price,
        )
        for exchange_rate in usd_krw_exchange_rate_list
    ]


@router.post("/treasury-yield/korea-1y", response_model=list[TreasuryYieldResponse])
@inject
def get_korea_1y_treasury_yield(
    request: TreasuryYieldRequest,
    market_indicator_service: MarketIndicatorService = Depends(
        Provide[Container.market_indicator_service]
    ),
):
    """한국 1년 만기 국채 수익률 조회 요청을 처리한다."""

    treasury_yield_list = market_indicator_service.get_korea_1y_treasury_yield(
        start_date=request.start_date, end_date=request.end_date
    )

    return [
        TreasuryYieldResponse(
            date=treasury_yield.date,
            yield_rate=treasury_yield.close_price,
        )
        for treasury_yield in treasury_yield_list
    ]


@router.post("/treasury-yield/korea-3y", response_model=list[TreasuryYieldResponse])
@inject
def get_korea_3y_treasury_yield(
    request: TreasuryYieldRequest,
    market_indicator_service: MarketIndicatorService = Depends(
        Provide[Container.market_indicator_service]
    ),
):
    """한국 3년 만기 국채 수익률 조회 요청을 처리한다."""

    treasury_yield_list = market_indicator_service.get_korea_3y_treasury_yield(
        start_date=request.start_date, end_date=request.end_date
    )

    return [
        TreasuryYieldResponse(
            date=treasury_yield.date,
            yield_rate=treasury_yield.close_price,
        )
        for treasury_yield in treasury_yield_list
    ]


@router.post("/treasury-yield/korea-5y", response_model=list[TreasuryYieldResponse])
@inject
def get_korea_5y_treasury_yield(
    request: TreasuryYieldRequest,
    market_indicator_service: MarketIndicatorService = Depends(
        Provide[Container.market_indicator_service]
    ),
):
    """한국 5년 만기 국채 수익률 조회 요청을 처리한다."""

    treasury_yield_list = market_indicator_service.get_korea_5y_treasury_yield(
        start_date=request.start_date, end_date=request.end_date
    )

    return [
        TreasuryYieldResponse(
            date=treasury_yield.date,
            yield_rate=treasury_yield.close_price,
        )
        for treasury_yield in treasury_yield_list
    ]


@router.post("/treasury-yield/korea-10y", response_model=list[TreasuryYieldResponse])
@inject
def get_korea_10y_treasury_yield(
    request: TreasuryYieldRequest,
    market_indicator_service: MarketIndicatorService = Depends(
        Provide[Container.market_indicator_service]
    ),
):
    """한국 10년 만기 국채 수익률 조회 요청을 처리한다."""

    treasury_yield_list = market_indicator_service.get_korea_10y_treasury_yield(
        start_date=request.start_date, end_date=request.end_date
    )

    return [
        TreasuryYieldResponse(
            date=treasury_yield.date,
            yield_rate=treasury_yield.close_price,
        )
        for treasury_yield in treasury_yield_list
    ]


@router.post("/treasury-yield/us-1y", response_model=list[TreasuryYieldResponse])
@inject
def get_us_1y_treasury_yield(
    request: TreasuryYieldRequest,
    market_indicator_service: MarketIndicatorService = Depends(
        Provide[Container.market_indicator_service]
    ),
):
    """미국 1년 만기 국채 수익률 조회 요청을 처리한다."""

    treasury_yield_list = market_indicator_service.get_us_1y_treasury_yield(
        start_date=request.start_date, end_date=request.end_date
    )

    return [
        TreasuryYieldResponse(
            date=treasury_yield.date,
            yield_rate=treasury_yield.close_price,
        )
        for treasury_yield in treasury_yield_list
    ]


@router.post("/treasury-yield/us-10y", response_model=list[TreasuryYieldResponse])
@inject
def get_us_10y_treasury_yield(
    request: TreasuryYieldRequest,
    market_indicator_service: MarketIndicatorService = Depends(
        Provide[Container.market_indicator_service]
    ),
):
    """미국 10년 만기 국채 수익률 조회 요청을 처리한다."""

    treasury_yield_list = market_indicator_service.get_us_10y_treasury_yield(
        start_date=request.start_date, end_date=request.end_date
    )

    return [
        TreasuryYieldResponse(
            date=treasury_yield.date,
            yield_rate=treasury_yield.close_price,
        )
        for treasury_yield in treasury_yield_list
    ]
