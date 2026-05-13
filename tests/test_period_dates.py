import unittest

from stock.service.indicator.period_dates import (
    calculate_period_fetch_start_date,
    normalize_period_end,
    normalize_period_start,
)


class PeriodDatesTest(unittest.TestCase):
    """기간별 대표 거래일과 조회 시작일 계산을 검증한다."""

    def test_normalizes_period_boundaries_to_krx_sessions(self):
        """휴장일이 포함된 기간 경계를 KRX 거래일로 보정한다."""

        self.assertEqual(normalize_period_start("20260101", "D"), "20260102")
        self.assertEqual(normalize_period_end("20260101", "D"), "20251230")
        self.assertEqual(normalize_period_start("20260101", "W"), "20251229")
        self.assertEqual(normalize_period_start("20250315", "M"), "20250304")
        self.assertEqual(normalize_period_start("20260115", "Y"), "20260102")

    def test_calculates_fetch_start_from_period_first_sessions(self):
        """W/M/Y fetch start도 첫 KRX 거래일 기준으로 계산한다."""

        self.assertEqual(
            calculate_period_fetch_start_date("20260401", "D", 14),
            "20260313",
        )
        self.assertEqual(
            calculate_period_fetch_start_date("20260330", "W", 14),
            "20251229",
        )
        self.assertEqual(
            calculate_period_fetch_start_date("20260401", "M", 14),
            "20250304",
        )
        self.assertEqual(
            calculate_period_fetch_start_date("20260102", "Y", 14),
            "20130102",
        )


if __name__ == "__main__":
    unittest.main()
