import unittest

from pydantic import ValidationError

from stock.domain.market import TreasuryYieldMaturity
from stock.interface.schema.common import DateRangeRequest


class MarketIndexSchemaTest(unittest.TestCase):
    """시장 지수의 공통 날짜 범위 요청을 검증한다."""

    def test_date_range_requires_explicit_dates_and_includes_descriptions(self):
        with self.assertRaises(ValidationError):
            DateRangeRequest()

        request = DateRangeRequest(start_date="20260401", end_date="20260407")
        self.assertEqual(request.start_date, "20260401")
        self.assertEqual(request.end_date, "20260407")
        self.assertEqual(
            DateRangeRequest.model_fields["start_date"].description,
            "조회 시작일입니다.",
        )
        self.assertEqual(
            DateRangeRequest.model_fields["end_date"].description,
            "조회 종료일입니다.",
        )

    def test_date_range_rejects_values_that_are_not_yyyymmdd(self):
        for field_name in ["start_date", "end_date"]:
            with self.subTest(field_name=field_name):
                with self.assertRaises(ValidationError):
                    DateRangeRequest(
                        **{
                            "start_date": "20260401",
                            "end_date": "20260407",
                            field_name: "2026-04-01",
                        }
                    )

    def test_date_range_rejects_impossible_calendar_dates(self):
        with self.assertRaisesRegex(
            ValidationError,
            "실제 존재하는 YYYYMMDD 날짜여야 합니다.",
        ):
            DateRangeRequest(start_date="20240230", end_date="20240301")

    def test_date_range_rejects_start_date_after_end_date(self):
        with self.assertRaisesRegex(
            ValidationError,
            "start_date는 end_date보다 늦을 수 없습니다.",
        ):
            DateRangeRequest(start_date="20260408", end_date="20260407")

    def test_treasury_maturity_enum_has_all_six_supported_paths(self):
        self.assertEqual(
            {maturity.value for maturity in TreasuryYieldMaturity},
            {
                "korea-1y",
                "korea-3y",
                "korea-5y",
                "korea-10y",
                "us-1y",
                "us-10y",
            },
        )

    def test_date_range_rejects_removed_or_unknown_fields(self):
        with self.assertRaises(ValidationError):
            DateRangeRequest(start_date="20260401", end_date="20260407", period="W")


if __name__ == "__main__":
    unittest.main()
