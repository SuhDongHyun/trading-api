import unittest

from pydantic import ValidationError

from stock.interface.schema.stock_quote import (
    DailyStockPriceRequest,
    HistoricalStockQuoteRequest,
    MacdRequest,
    MacdSignalRequest,
    MovingAverageRequest,
    RsiRequest,
    RsiSignalRequest,
    StockQuoteRequest,
    StockInfoRequest,
)


class StockQuoteSchemaTest(unittest.TestCase):
    """시세 조회 요청 스키마 기본값과 validation을 검증한다."""

    def test_request_schemas_inherit_common_field_models(self):
        """요청 모델은 공통 필드 모델을 상속한다."""

        self.assertTrue(issubclass(StockInfoRequest, StockQuoteRequest))

        historical_request_classes = [
            DailyStockPriceRequest,
            MovingAverageRequest,
            RsiRequest,
            RsiSignalRequest,
            MacdRequest,
            MacdSignalRequest,
        ]

        for request_class in historical_request_classes:
            self.assertTrue(issubclass(request_class, HistoricalStockQuoteRequest))

        self.assertTrue(issubclass(RsiSignalRequest, RsiRequest))
        self.assertTrue(issubclass(MacdSignalRequest, MacdRequest))

    def test_request_schemas_provide_controller_defaults(self):
        """시장, 종목, 조회 기간 기본값이 자동으로 채워진다."""

        request_classes = [
            StockInfoRequest,
            DailyStockPriceRequest,
            MovingAverageRequest,
            RsiRequest,
            RsiSignalRequest,
            MacdRequest,
            MacdSignalRequest,
        ]

        for request_class in request_classes:
            request = request_class()

            self.assertEqual(request.market, "J")
            self.assertEqual(request.code, "005930")

            if hasattr(request, "start_date"):
                self.assertEqual(request.start_date, "20260101")
                self.assertEqual(request.end_date, "20260107")

    def test_period_request_schemas_allow_only_supported_period_codes(self):
        """기간 코드는 일/주/月/年 코드만 허용한다."""

        request_classes = [
            DailyStockPriceRequest,
            MovingAverageRequest,
            RsiRequest,
            RsiSignalRequest,
            MacdRequest,
            MacdSignalRequest,
        ]

        for request_class in request_classes:
            for period in ["D", "W", "M", "Y"]:
                self.assertEqual(request_class(period=period).period, period)

            with self.assertRaises(ValidationError):
                request_class(period="Q")

    def test_window_fields_reject_values_below_one(self):
        """window 계열 파라미터는 1 이상이어야 한다."""

        invalid_cases = [
            (MovingAverageRequest, {"window": 0}),
            (RsiRequest, {"rsi_window": 0}),
            (RsiSignalRequest, {"rsi_window": 0}),
            (RsiSignalRequest, {"ema_window": 0}),
            (MacdRequest, {"ema_short_window": 0}),
            (MacdRequest, {"ema_long_window": 0}),
            (MacdSignalRequest, {"ema_short_window": 0}),
            (MacdSignalRequest, {"ema_long_window": 0}),
            (MacdSignalRequest, {"ema_window": 0}),
        ]

        for request_class, kwargs in invalid_cases:
            with self.assertRaises(ValidationError):
                request_class(**kwargs)

    def test_request_schema_fields_include_descriptions(self):
        """요청 필드는 OpenAPI 문서용 description을 가진다."""

        request_classes = [
            StockInfoRequest,
            DailyStockPriceRequest,
            MovingAverageRequest,
            RsiRequest,
            RsiSignalRequest,
            MacdRequest,
            MacdSignalRequest,
        ]

        for request_class in request_classes:
            for field in request_class.model_fields.values():
                self.assertIsNotNone(field.description)

    def test_historical_requests_reject_invalid_date_ranges(self):
        """조회 날짜는 YYYYMMDD 형식이며 시작일이 종료일보다 늦을 수 없다."""

        with self.assertRaises(ValidationError):
            HistoricalStockQuoteRequest(start_date="2026-01-01")

        with self.assertRaisesRegex(
            ValidationError,
            "start_date는 end_date보다 늦을 수 없습니다.",
        ):
            HistoricalStockQuoteRequest(
                start_date="20260108",
                end_date="20260107",
            )


if __name__ == "__main__":
    unittest.main()
