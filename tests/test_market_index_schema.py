import unittest

from pydantic import ValidationError

from stock.interface.schema.market_index import (
    DateRangeRequest,
    KosdaqIndexRequest,
    KospiIndexRequest,
    SP500IndexRequest,
    TreasuryYieldRequest,
    UsdKrwExchangeRateRequest,
    VIXIndexRequest,
)


class MarketIndexSchemaTest(unittest.TestCase):
    """시장 지수 요청 스키마의 공통 날짜 범위 validation을 검증한다."""

    def test_date_range_requests_inherit_common_defaults_and_descriptions(self):
        request_classes = [
            VIXIndexRequest,
            UsdKrwExchangeRateRequest,
            TreasuryYieldRequest,
            SP500IndexRequest,
            KospiIndexRequest,
            KosdaqIndexRequest,
        ]

        for request_class in request_classes:
            self.assertTrue(issubclass(request_class, DateRangeRequest))

            request = request_class()
            self.assertEqual(request.start_date, "20260101")
            self.assertEqual(request.end_date, "20260107")
            self.assertEqual(
                request_class.model_fields["start_date"].description,
                "조회 시작일입니다.",
            )
            self.assertEqual(
                request_class.model_fields["end_date"].description,
                "조회 종료일입니다.",
            )

    def test_date_range_rejects_values_that_are_not_yyyymmdd(self):
        for field_name in ["start_date", "end_date"]:
            with self.assertRaises(ValidationError):
                DateRangeRequest(**{field_name: "2026-01-01"})

    def test_date_range_rejects_start_date_after_end_date(self):
        with self.assertRaisesRegex(
            ValidationError,
            "start_date는 end_date보다 늦을 수 없습니다.",
        ):
            DateRangeRequest(start_date="20260108", end_date="20260107")


if __name__ == "__main__":
    unittest.main()
