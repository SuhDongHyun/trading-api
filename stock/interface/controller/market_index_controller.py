from fastapi import APIRouter, Depends
from dependency_injector.wiring import Provide, inject

from container import Container
from stock.domain.market import TreasuryYieldMaturity
from stock.interface.schema.common import DateRangeRequest
from stock.interface.schema.market_index import (
    DomesticMarketIndexResponse,
    FearAndGreedIndexResponse,
    OverseasMarketIndexResponse,
    StockMetaInfoResponse,
    TreasuryYieldResponse,
    VIXIndexResponse,
    VkospiIndexResponse,
)
from stock.service.market_index_service import MarketIndexService

router = APIRouter(prefix="/market-index", tags=["market-index"])


@router.get("/korea-stock-list", response_model=list[StockMetaInfoResponse])
@inject
def get_korea_stock_list(
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    values = market_index_service.get_korea_stock_list()
    return [StockMetaInfoResponse.model_validate(value) for value in values]


@router.get("/fear-and-greed-index", response_model=FearAndGreedIndexResponse)
@inject
def get_fear_and_greed_index(
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    value = market_index_service.get_fear_and_greed_index()
    return FearAndGreedIndexResponse.model_validate(value)


@router.post("/vix-index", response_model=list[VIXIndexResponse])
@inject
def get_vix_index(
    request: DateRangeRequest,
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    values = market_index_service.get_vix_index(request.start_date, request.end_date)
    return [VIXIndexResponse.model_validate(value) for value in values]


@router.post("/vkospi-index", response_model=list[VkospiIndexResponse])
@inject
def get_vkospi_index(
    request: DateRangeRequest,
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    values = market_index_service.get_vkospi_index(request.start_date, request.end_date)
    return [VkospiIndexResponse.model_validate(value) for value in values]


@router.post("/usd-krw-exchange-rate", response_model=list[OverseasMarketIndexResponse])
@inject
def get_usd_krw_exchange_rate(
    request: DateRangeRequest,
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    values = market_index_service.get_usd_krw_exchange_rate(
        request.start_date, request.end_date
    )
    return [OverseasMarketIndexResponse.model_validate(value) for value in values]


@router.post("/treasury-yield/{maturity}", response_model=list[TreasuryYieldResponse])
@inject
def get_treasury_yield(
    maturity: TreasuryYieldMaturity,
    request: DateRangeRequest,
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    values = market_index_service.get_treasury_yield(
        maturity, request.start_date, request.end_date
    )
    return [TreasuryYieldResponse.model_validate(value) for value in values]


@router.post("/sp500-index", response_model=list[OverseasMarketIndexResponse])
@inject
def get_sp500_index(
    request: DateRangeRequest,
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    values = market_index_service.get_sp500_index(request.start_date, request.end_date)
    return [OverseasMarketIndexResponse.model_validate(value) for value in values]


@router.post("/kospi-index", response_model=list[DomesticMarketIndexResponse])
@inject
def get_kospi_index(
    request: DateRangeRequest,
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    values = market_index_service.get_kospi_index(request.start_date, request.end_date)
    return [DomesticMarketIndexResponse.model_validate(value) for value in values]


@router.post("/kosdaq-index", response_model=list[DomesticMarketIndexResponse])
@inject
def get_kosdaq_index(
    request: DateRangeRequest,
    market_index_service: MarketIndexService = Depends(
        Provide[Container.market_index_service]
    ),
):
    values = market_index_service.get_kosdaq_index(request.start_date, request.end_date)
    return [DomesticMarketIndexResponse.model_validate(value) for value in values]
