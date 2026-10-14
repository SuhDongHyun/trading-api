import unittest

from pydantic import ValidationError

from stock.interface.schema.stock_quote import (
    HistoricalStockQuoteRequest,
    MacdRequest,
    MacdSignalRequest,
    MovingAverageRequest,
    RsiRequest,
    RsiSignalRequest,
    StockQuoteRequest,
)


class StockQuoteSchemaTest(unittest.TestCase):
    """시세 조회 요청 스키마 기본값과 validation을 검증한다."""

    def test_request_schemas_inherit_common_field_models(self):
        """요청 모델은 공통 필드 모델을 상속한다."""

        historical_request_classes = [
            MovingAverageRequest,
            RsiRequest,
            RsiSignalRequest,
            MacdRequest,
            MacdSignalRequest,
        ]

        self.assertTrue(issubclass(HistoricalStockQuoteRequest, StockQuoteRequest))
        for request_class in historical_request_classes:
            self.assertTrue(issubclass(request_class, HistoricalStockQuoteRequest))

        self.assertTrue(issubclass(RsiSignalRequest, RsiRequest))
        self.assertTrue(issubclass(MacdSignalRequest, MacdRequest))

    def test_request_schemas_provide_controller_defaults(self):
        """시장, 종목, 조회 기간 기본값이 자동으로 채워진다."""

        request_classes = [
            StockQuoteRequest,
            HistoricalStockQuoteRequest,
            MovingAverageRequest,
            RsiRequest,
            RsiSignalRequest,
            MacdRequest,
            MacdSignalRequest,
        ]

        for request_class in request_classes:
            request = (
                request_class(start_date="20260401", end_date="20260407")
                if issubclass(request_class, HistoricalStockQuoteRequest)
                else request_class()
            )

            self.assertEqual(request.market, "J")
            self.assertEqual(request.code, "005930")

            if hasattr(request, "start_date"):
                self.assertEqual(request.start_date, "20260401")
                self.assertEqual(request.end_date, "20260407")

    def test_historical_request_schemas_do_not_expose_period(self):
        """과거 시세 요청은 일봉으로 고정되어 period 필드를 노출하지 않는다."""

        request_classes = [
            MovingAverageRequest,
            RsiRequest,
            RsiSignalRequest,
            MacdRequest,
            MacdSignalRequest,
        ]

        for request_class in request_classes:
            self.assertNotIn("period", request_class.model_fields)

    def test_window_fields_reject_values_below_their_minimum(self):
        """EMA 창은 2 이상, 나머지 계산 창은 1 이상이어야 한다."""

        invalid_cases = [
            (MovingAverageRequest, {"window": 0}),
            (RsiRequest, {"rsi_window": 0}),
            (RsiSignalRequest, {"rsi_window": 0}),
            (RsiSignalRequest, {"ema_window": 1}),
            (MacdRequest, {"ema_short_window": 1}),
            (MacdRequest, {"ema_long_window": 1}),
            (MacdSignalRequest, {"ema_short_window": 1}),
            (MacdSignalRequest, {"ema_long_window": 1}),
            (MacdSignalRequest, {"ema_window": 1}),
        ]

        for request_class, kwargs in invalid_cases:
            with self.assertRaises(ValidationError):
                request_class(**kwargs)

    def test_request_schema_fields_include_descriptions(self):
        """요청 필드는 OpenAPI 문서용 description을 가진다."""

        request_classes = [
            StockQuoteRequest,
            HistoricalStockQuoteRequest,
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
            HistoricalStockQuoteRequest(start_date="2026-01-01", end_date="20260110")

        with self.assertRaisesRegex(
            ValidationError,
            "start_date는 end_date보다 늦을 수 없습니다.",
        ):
            HistoricalStockQuoteRequest(
                start_date="20260108",
                end_date="20260107",
            )

    def test_requests_reject_extra_fields_including_removed_period(self):
        with self.assertRaises(ValidationError):
            HistoricalStockQuoteRequest(
                start_date="20260401", end_date="20260407", period="W"
            )

    def test_historical_dates_are_required(self):
        with self.assertRaises(ValidationError):
            HistoricalStockQuoteRequest()


if __name__ == "__main__":
    unittest.main()
