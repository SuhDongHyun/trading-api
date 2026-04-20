import uvicorn
from fastapi import FastAPI

from container import Container
from stock.interface.controller.account_controller import router as account_router
from stock.interface.controller.stock_quote_controller import (
    router as stock_quote_router,
)

app = FastAPI()
app.include_router(account_router)
app.include_router(stock_quote_router)

container = Container()
container.wire

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=9999, reload=True)
