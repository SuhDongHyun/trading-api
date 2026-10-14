from unittest.mock import Mock

from pytest import approx

from common.min_interval_throttle import MinIntervalThrottle


def test_min_interval_throttle_waits_until_the_shared_interval_has_elapsed():
    """공용 throttle은 마지막 요청 슬롯과 최소 간격을 유지한다."""

    clock = Mock(side_effect=[100.0, 100.05, 100.15])
    wait = Mock()
    throttle = MinIntervalThrottle(0.15, clock=clock, wait=wait)

    throttle.acquire()
    throttle.acquire()

    wait.assert_called_once_with(approx(0.1))
