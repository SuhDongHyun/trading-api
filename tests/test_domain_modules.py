import unittest


class DomainModuleBoundaryTest(unittest.TestCase):
    """주식 도메인 데이터 클래스의 모듈 경계를 검증한다."""

    def test_price_model_is_part_of_stock_module(self):
        """주식 가격 이력 모델은 주식 도메인 모듈에서 가져온다."""

        from stock.domain.indicator import MovingAverage, Rsi, RsiSignal
        from stock.domain.stock import DailyStockPrice, StockInfo

        self.assertEqual(DailyStockPrice.__module__, "stock.domain.stock")
        self.assertEqual(MovingAverage.__module__, "stock.domain.indicator")
        self.assertEqual(Rsi.__module__, "stock.domain.indicator")
        self.assertEqual(RsiSignal.__module__, "stock.domain.indicator")
        self.assertEqual(StockInfo.__module__, "stock.domain.stock")


if __name__ == "__main__":
    unittest.main()
