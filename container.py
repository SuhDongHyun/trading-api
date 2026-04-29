from dependency_injector import containers, providers

from stock.infra.kis.kis_client import KISClient
from stock.service.account_service import AccountService
from stock.service.stock_quote_service import StockQuoteService


class Container(containers.DeclarativeContainer):
    """FastAPI 컨트롤러에 주입할 클라이언트와 서비스 객체를 구성한다."""

    wiring_config = containers.WiringConfiguration(
        packages=["stock.interface.controller"]
    )

    kis_client = providers.Factory(KISClient)
    account_service = providers.Factory(AccountService, api_client=kis_client)
    stock_quote_service = providers.Factory(StockQuoteService, api_client=kis_client)
