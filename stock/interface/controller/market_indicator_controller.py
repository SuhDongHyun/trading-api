from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from container import Container
from stock.service.market_indicator_service import MarketIndicatorService
from stock.interface.schema.market_indicator import (
    FearAndGreedIndexResponse,
    VIXIndexRequest,
    VIXIndexResponse,
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
