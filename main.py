from contextlib import asynccontextmanager
import logging
from urllib.parse import urlsplit

import requests
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from bitcoin.interface.controller.quotation_controller import router as bitcoin_router
from common.exchange_calendar import get_krx_calendar
from container import Container
from stock.domain.exceptions import AppError
from stock.interface.controller.account_controller import router as account_router
from stock.interface.controller.stock_news_controller import (
    router as stock_news_router,
)
from stock.interface.controller.stock_quote_controller import (
    router as stock_quote_router,
)
from stock.interface.controller.market_index_controller import (
    router as market_index_router,
)

logger = logging.getLogger(__name__)

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s - %(message)s"
HEALTH_PATH = "/health"


class HealthCheckAccessFilter(logging.Filter):
    """Docker HEALTHCHECK가 주기적으로 남기는 access log를 제외한다."""

    def filter(self, record: logging.LogRecord) -> bool:
        args = record.args
        if isinstance(args, tuple) and len(args) >= 3:
            return str(args[2]).split("?", 1)[0] != HEALTH_PATH
        return True


def configure_logging() -> None:
    """앱 로거가 시간·레벨·로거 이름과 함께 INFO 이상을 출력하게 한다.

    uvicorn 로거는 자체 handler를 쓰고 root로 전파하지 않으므로 중복 출력되지 않는다.
    """

    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    access_logger = logging.getLogger("uvicorn.access")
    if not any(isinstance(f, HealthCheckAccessFilter) for f in access_logger.filters):
        access_logger.addFilter(HealthCheckAccessFilter())


configure_logging()


@asynccontextmanager
async def lifespan(app):
    warm_up_krx_calendar()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(account_router)
app.include_router(stock_news_router)
app.include_router(stock_quote_router)
app.include_router(market_index_router)
app.include_router(bitcoin_router)


@app.get(HEALTH_PATH, include_in_schema=False)
def health() -> dict[str, str]:
    """프로세스가 요청을 처리할 수 있는지만 확인하며 외부 API는 호출하지 않는다."""

    return {"status": "ok"}


def warm_up_krx_calendar():
    """서버 시작 시 KRX 캘린더를 미리 생성한다."""

    get_krx_calendar()


def register_exception_handlers(app: FastAPI) -> None:
    """외부 실패를 서버 오류와 구분하고, 민감정보를 뺀 원인만 로그에 남긴다."""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.error(
            "Application error status=%s type=%s diagnostic=%s",
            exc.status_code,
            type(exc).__name__,
            exc.diagnostic,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": str(exc)},
        )

    @app.exception_handler(requests.RequestException)
    async def request_error_handler(
        request: Request, exc: requests.RequestException
    ) -> JSONResponse:
        upstream_request = exc.request or (
            exc.response.request if exc.response is not None else None
        )
        response = exc.response
        request_url = upstream_request.url if upstream_request is not None else ""
        path = urlsplit(request_url).path
        headers = upstream_request.headers if upstream_request is not None else {}
        tr_id = headers.get("tr_id")
        status_code = response.status_code if response is not None else None
        response_body = response.text[:500] if response is not None else ""

        logger.error(
            "External HTTP request failed type=%s method=%s path=%s status=%s "
            "tr_id=%s body=%s",
            type(exc).__name__,
            upstream_request.method if upstream_request is not None else None,
            path,
            status_code,
            tr_id,
            response_body,
        )

        return JSONResponse(
            status_code=502,
            content={"detail": "외부 API 요청에 실패했습니다."},
        )


container = Container()
register_exception_handlers(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9999, reload=True)
