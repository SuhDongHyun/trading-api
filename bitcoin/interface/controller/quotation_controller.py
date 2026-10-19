from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from bitcoin.interface.schema.quotation import (
    CandleResponse,
    CandlesRequest,
    DayCandlesRequest,
    DayCandleResponse,
    MinuteCandleUnit,
    MinuteCandleResponse,
    OrderbookInstrumentResponse,
    OrderbookInstrumentsRequest,
    OrderbookRequest,
    OrderbookResponse,
    PeriodCandleResponse,
    QuoteTickerRequest,
    TickerRequest,
    TickerResponse,
    TradeResponse,
    TradesRequest,
    TradingPairResponse,
    TradingPairsRequest,
)
from bitcoin.service.quotation_services import (
    CandleService,
    OrderbookInstrumentService,
    OrderbookService,
    QuoteTickerService,
    TickerService,
    TradeService,
    TradingPairService,
)
from container import Container

router = APIRouter(prefix="/bitcoin", tags=["bitcoin"])


@router.post("/trading-pairs", response_model=list[TradingPairResponse])
@inject
def get_trading_pairs(
    request: TradingPairsRequest,
    service: TradingPairService = Depends(Provide[Container.trading_pair_service]),
):
    values = service.get_trading_pairs(request.is_details)
    return [TradingPairResponse.model_validate(value) for value in values]


@router.post("/ticker", response_model=list[TickerResponse])
@inject
def get_tickers(
    request: TickerRequest,
    service: TickerService = Depends(Provide[Container.ticker_service]),
):
    values = service.get_tickers(request.markets)
    return [TickerResponse.model_validate(value) for value in values]


@router.post("/ticker/quote", response_model=list[TickerResponse])
@inject
def get_quote_tickers(
    request: QuoteTickerRequest,
    service: QuoteTickerService = Depends(Provide[Container.quote_ticker_service]),
):
    values = service.get_tickers(request.quote_currencies)
    return [TickerResponse.model_validate(value) for value in values]


@router.post("/orderbook", response_model=list[OrderbookResponse])
@inject
def get_orderbooks(
    request: OrderbookRequest,
    service: OrderbookService = Depends(Provide[Container.orderbook_service]),
):
    values = service.get_orderbooks(
        request.markets, level=request.level, count=request.count
    )
    return [OrderbookResponse.model_validate(value) for value in values]


@router.post("/orderbook/instruments", response_model=list[OrderbookInstrumentResponse])
@inject
def get_orderbook_instruments(
    request: OrderbookInstrumentsRequest,
    service: OrderbookInstrumentService = Depends(
        Provide[Container.orderbook_instrument_service]
    ),
):
    values = service.get_orderbook_instruments(request.markets)
    return [OrderbookInstrumentResponse.model_validate(value) for value in values]


@router.post("/trades", response_model=list[TradeResponse])
@inject
def get_trades(
    request: TradesRequest,
    service: TradeService = Depends(Provide[Container.trade_service]),
):
    values = service.get_trades(
        market=request.market,
        to=request.to,
        count=request.count,
        cursor=request.cursor,
        days_ago=request.days_ago,
    )
    return [TradeResponse.model_validate(value) for value in values]


@router.post("/candles/seconds", response_model=list[CandleResponse])
@inject
def get_seconds_candles(
    request: CandlesRequest,
    service: CandleService = Depends(Provide[Container.candle_service]),
):
    values = service.get_seconds_candles(
        market=request.market, to=request.to, count=request.count
    )
    return [CandleResponse.model_validate(value) for value in values]


@router.post("/candles/minutes/{unit}", response_model=list[MinuteCandleResponse])
@inject
def get_minute_candles(
    unit: MinuteCandleUnit,
    request: CandlesRequest,
    service: CandleService = Depends(Provide[Container.candle_service]),
):
    values = service.get_minute_candles(
        int(unit), market=request.market, to=request.to, count=request.count
    )
    return [MinuteCandleResponse.model_validate(value) for value in values]


@router.post("/candles/days", response_model=list[DayCandleResponse])
@inject
def get_day_candles(
    request: DayCandlesRequest,
    service: CandleService = Depends(Provide[Container.candle_service]),
):
    values = service.get_day_candles(
        market=request.market,
        to=request.to,
        count=request.count,
        converting_price_unit=request.converting_price_unit,
    )
    return [DayCandleResponse.model_validate(value) for value in values]


@router.post("/candles/weeks", response_model=list[PeriodCandleResponse])
@inject
def get_week_candles(
    request: CandlesRequest,
    service: CandleService = Depends(Provide[Container.candle_service]),
):
    values = service.get_week_candles(
        market=request.market, to=request.to, count=request.count
    )
    return [PeriodCandleResponse.model_validate(value) for value in values]


@router.post("/candles/months", response_model=list[PeriodCandleResponse])
@inject
def get_month_candles(
    request: CandlesRequest,
    service: CandleService = Depends(Provide[Container.candle_service]),
):
    values = service.get_month_candles(
        market=request.market, to=request.to, count=request.count
    )
    return [PeriodCandleResponse.model_validate(value) for value in values]


@router.post("/candles/years", response_model=list[PeriodCandleResponse])
@inject
def get_year_candles(
    request: CandlesRequest,
    service: CandleService = Depends(Provide[Container.candle_service]),
):
    values = service.get_year_candles(
        market=request.market, to=request.to, count=request.count
    )
    return [PeriodCandleResponse.model_validate(value) for value in values]
