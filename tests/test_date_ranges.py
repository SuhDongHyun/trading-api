import unittest

from stock.service.indicator.date_ranges import (
    calculate_daily_fetch_start_date,
    normalize_daily_end_date,
    normalize_daily_start_date,
)


class DailyDateRangesTest(unittest.TestCase):
    """일봉 지표 날짜를 KRX 거래일 기준으로 보정하는 동작을 검증한다."""

    def test_normalizes_daily_range_to_krx_sessions(self):
        """휴장일 시작은 다음 거래일, 종료는 직전 거래일로 보정한다."""

        self.assertEqual(normalize_daily_start_date("20260101"), "20260102")
        self.assertEqual(normalize_daily_end_date("20260101"), "20251230")

    def test_calculates_fetch_start_from_daily_trading_sessions(self):
        """일봉 window는 달력 날짜가 아니라 선행 KRX 거래일 수로 계산한다."""

        self.assertEqual(calculate_daily_fetch_start_date("20260401", 14), "20260313")
        self.assertEqual(calculate_daily_fetch_start_date("20260401", 1), "20260401")


if __name__ == "__main__":
    unittest.main()
