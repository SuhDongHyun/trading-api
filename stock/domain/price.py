from dataclasses import dataclass


@dataclass
class DailyStockPriceSummary:
    """일봉 조회 결과에 공통으로 붙는 종목 식별 정보."""

    name: str
    code: str


@dataclass
class DailyStockPrice:
    """특정 거래일의 OHLC 가격과 거래대금 정보."""

    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    accumulated_volume: int
    accumulated_trading_value: float
    price_diff: float
    price_diff_sign: str
    change_flag: str


@dataclass
class DailyStockPriceResult:
    """일봉 요약 정보와 날짜별 가격 목록."""

    summary: DailyStockPriceSummary
    prices: list[DailyStockPrice]

    def __iter__(self):
        """외부 응답 계층이 가격 목록만 순회할 수 있도록 한다."""

        return iter(self.prices)

    def __len__(self) -> int:
        """가격 목록 길이를 그대로 노출한다."""

        return len(self.prices)

    def __getitem__(self, index: int) -> DailyStockPrice:
        """가격 목록 인덱스 접근을 그대로 위임한다."""

        return self.prices[index]
