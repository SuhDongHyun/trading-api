from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from container import Container
from stock.interface.schema.stock_news import (
    StockNewsRequest,
    StockNewsResponse,
)
from stock.service.stock_news_service import StockNewsService

router = APIRouter(prefix="/stock_news", tags=["stock_news"])


@router.post("", response_model=list[StockNewsResponse])
@inject
def get_stock_news(
    request: StockNewsRequest,
    stock_news_service: StockNewsService = Depends(
        Provide[Container.stock_news_service]
    ),
):
    """뉴스 조회 요청을 처리하고 응답 스키마로 변환한다."""

    news_list = stock_news_service.get_total_news(
        code=request.code,
        search_date=request.search_date,
        search_time=request.search_time,
    )

    return [
        StockNewsResponse(
            title=news.title,
            source=news.source,
            published_at=news.published_at,
        )
        for news in news_list
    ]
