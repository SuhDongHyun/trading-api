from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from container import Container
from stock.service.market_index_service import MarketIndexService
from stock.interface.schema.market_index import (
    FearAndGreedIndexResponse,
    VIXIndexRequest,
    VIXIndexResponse,
    VkospiIndexRequest,
    VkospiIndexResponse,
    UsdKrwExchangeRateRequest,
    UsdKrwExchangeRateResponse,
    TreasuryYieldRequest,
    TreasuryYieldResponse,
    SP500IndexRequest,
    SP500IndexResponse,
    KospiIndexRequest,
    KospiIndexResponse,
    KosdaqIndexRequest,
    KosdaqIndexResponse,
)

router = APIRouter(prefix="/market-indicator", tags=["market-indicator"])


@router.get("/fear-and-greed-index", response_model=FearAndGreedIndexResponse)
@inject
def get_fear_and_greed_index(
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    """공포탐욕지수 조회 요청을 처리한다."""

    fear_and_greed_index = market_index_service.get_fear_and_greed_index()

    return FearAndGreedIndexResponse(
        value=fear_and_greed_index.value,
        condition=fear_and_greed_index.condition,
        updated_at=fear_and_greed_index.updated_at,
    )


@router.post("/vix-index", response_model=list[VIXIndexResponse])
@inject
def get_vix_index(
    request: VIXIndexRequest,
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    """VIX 지수 조회 요청을 처리한다."""

    vix_index_list = market_index_service.get_vix_index(
        start_date=request.start_date, end_date=request.end_date
    )

    return [
        VIXIndexResponse(
            date=vix_index.date,
            value=vix_index.value,
        )
        for vix_index in vix_index_list
    ]


@router.post("/vkospi-index", response_model=list[VkospiIndexResponse])
@inject
def get_vkospi_index(
    request: VkospiIndexRequest,
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    """VKOSPI 지수 조회 요청을 처리한다."""

    vkospi_index_list = market_index_service.get_vkospi_index(
        start_date=request.start_date, end_date=request.end_date
    )

    return [
        VkospiIndexResponse(
            date=vkospi_index.date,
            open_price=vkospi_index.open_price,
            high_price=vkospi_index.high_price,
            low_price=vkospi_index.low_price,
            close_price=vkospi_index.close_price,
            price_diff=vkospi_index.price_diff,
            price_diff_rate=vkospi_index.price_diff_rate,
        )
        for vkospi_index in vkospi_index_list
    ]


@router.post("/usd-krw-exchange-rate", response_model=list[UsdKrwExchangeRateResponse])
@inject
def get_usd_krw_exchange_rate(
    request: UsdKrwExchangeRateRequest,
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    """USD/KRW 환율 조회 요청을 처리한다."""

    usd_krw_exchange_rate_list = market_index_service.get_usd_krw_exchange_rate(
        start_date=request.start_date, end_date=request.end_date
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
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    """한국 1년 만기 국채 수익률 조회 요청을 처리한다."""

    treasury_yield_list = market_index_service.get_korea_1y_treasury_yield(
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
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    """한국 3년 만기 국채 수익률 조회 요청을 처리한다."""

    treasury_yield_list = market_index_service.get_korea_3y_treasury_yield(
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
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    """한국 5년 만기 국채 수익률 조회 요청을 처리한다."""

    treasury_yield_list = market_index_service.get_korea_5y_treasury_yield(
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
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    """한국 10년 만기 국채 수익률 조회 요청을 처리한다."""

    treasury_yield_list = market_index_service.get_korea_10y_treasury_yield(
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
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    """미국 1년 만기 국채 수익률 조회 요청을 처리한다."""

    treasury_yield_list = market_index_service.get_us_1y_treasury_yield(
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
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    """미국 10년 만기 국채 수익률 조회 요청을 처리한다."""

    treasury_yield_list = market_index_service.get_us_10y_treasury_yield(
        start_date=request.start_date, end_date=request.end_date
    )

    return [
        TreasuryYieldResponse(
            date=treasury_yield.date,
            yield_rate=treasury_yield.close_price,
        )
        for treasury_yield in treasury_yield_list
    ]


@router.post("/sp500-index", response_model=list[SP500IndexResponse])
@inject
def get_sp500_index(
    request: SP500IndexRequest,
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    """S&P 500 지수 조회 요청을 처리한다."""

    sp500_index_list = market_index_service.get_sp500_index(
        start_date=request.start_date, end_date=request.end_date
    )

    return [
        SP500IndexResponse(
            date=sp500_index.date,
            open_price=sp500_index.open_price,
            high_price=sp500_index.high_price,
            low_price=sp500_index.low_price,
            close_price=sp500_index.close_price,
        )
        for sp500_index in sp500_index_list
    ]


@router.post("/kospi-index", response_model=list[KospiIndexResponse])
@inject
def get_kospi_index(
    request: KospiIndexRequest,
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    """KOSPI 지수 조회 요청을 처리한다."""

    kospi_index_list = market_index_service.get_kospi_index(
        start_date=request.start_date, end_date=request.end_date
    )

    return [
        KospiIndexResponse(
            date=kospi_index.date,
            open_price=kospi_index.open_price,
            high_price=kospi_index.high_price,
            low_price=kospi_index.low_price,
            close_price=kospi_index.close_price,
            price_diff=kospi_index.price_diff,
            price_diff_rate=kospi_index.price_diff_rate,
            volume=kospi_index.volume,
            trading_value=kospi_index.trading_value,
        )
        for kospi_index in kospi_index_list
    ]


@router.post("/kosdaq-index", response_model=list[KosdaqIndexResponse])
@inject
def get_kosdaq_index(
    request: KosdaqIndexRequest,
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    """KOSDAQ 지수 조회 요청을 처리한다."""

    kosdaq_index_list = market_index_service.get_kosdaq_index(
        start_date=request.start_date, end_date=request.end_date
    )

    return [
        KosdaqIndexResponse(
            date=kosdaq_index.date,
            open_price=kosdaq_index.open_price,
            high_price=kosdaq_index.high_price,
            low_price=kosdaq_index.low_price,
            close_price=kosdaq_index.close_price,
            price_diff=kosdaq_index.price_diff,
            price_diff_rate=kosdaq_index.price_diff_rate,
            volume=kosdaq_index.volume,
            trading_value=kosdaq_index.trading_value,
        )
        for kosdaq_index in kosdaq_index_list
    ]
