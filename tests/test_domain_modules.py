import unittest


class DomainModuleBoundaryTest(unittest.TestCase):
    """주식 도메인 데이터 클래스의 모듈 경계를 검증한다."""

    def test_price_and_indicator_models_are_split_from_stock_module(self):
        """가격 이력과 지표 결과 모델은 전용 도메인 모듈에서 가져온다."""

        from stock.domain.indicator import RsiResult, SlowStochasticResult
        from stock.domain.price import DailyStockPrice, DailyStockPriceResult
        from stock.domain.stock import StockInfo

        self.assertEqual(DailyStockPrice.__module__, "stock.domain.price")
        self.assertEqual(DailyStockPriceResult.__module__, "stock.domain.price")
        self.assertEqual(RsiResult.__module__, "stock.domain.indicator")
        self.assertEqual(SlowStochasticResult.__module__, "stock.domain.indicator")
        self.assertEqual(StockInfo.__module__, "stock.domain.stock")


if __name__ == "__main__":
    unittest.main()
