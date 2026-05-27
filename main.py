from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from common.exchange_calendar import get_krx_calendar
from container import Container
from stock.interface.controller.account_controller import router as account_router
from stock.interface.controller.stock_news_controller import (
    router as stock_news_router,
)
from stock.interface.controller.stock_quote_controller import (
    router as stock_quote_router,
)


@asynccontextmanager
async def lifespan(app):
    warm_up_krx_calendar()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(account_router)
app.include_router(stock_news_router)
app.include_router(stock_quote_router)


def warm_up_krx_calendar():
    """서버 시작 시 KRX 캘린더를 미리 생성한다."""

    get_krx_calendar()


container = Container()
container.wire

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=9999, reload=True)
