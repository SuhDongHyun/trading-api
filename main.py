import uvicorn
from fastapi import FastAPI

from container import Container
from stock.interface.controller.account_controller import router as account_router

app = FastAPI()
app.include_router(account_router)

container = Container()
container.wire

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=9999, reload=True)
