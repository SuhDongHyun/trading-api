import unittest

from common.exchange_calendar import get_krx_calendar
from stock.infra.kis.kis_util import MAX_CALLABLE_DATES, split_date_range


class KisUtilTest(unittest.TestCase):
    """KIS 일봉 조회 구간이 거래일 100개를 넘지 않도록 분할되는지 검증한다."""

    def test_splits_daily_ranges_by_krx_sessions(self):
        start_date = "20240101"
        end_date = "20240630"
        calendar = get_krx_calendar()
        sessions = calendar.sessions_in_range(start_date, end_date)

        ranges = split_date_range(start_date, end_date)

        self.assertEqual(len(ranges), 2)
        self.assertEqual(ranges[0][0], sessions[0].strftime("%Y%m%d"))
        self.assertEqual(
            ranges[0][1], sessions[MAX_CALLABLE_DATES - 1].strftime("%Y%m%d")
        )
        self.assertEqual(ranges[1][0], sessions[MAX_CALLABLE_DATES].strftime("%Y%m%d"))
        self.assertEqual(ranges[1][1], sessions[-1].strftime("%Y%m%d"))


if __name__ == "__main__":
    unittest.main()
