from unittest.mock import Mock, call

import pytest
from requests import ConnectionError, HTTPError, ReadTimeout

from common.network_retry import send_with_network_retry


def test_returns_first_result_without_waiting():
    send = Mock(return_value="ok")
    sleep = Mock()

    assert send_with_network_retry(send, label="test", sleep=sleep) == "ok"

    send.assert_called_once_with()
    sleep.assert_not_called()


@pytest.mark.parametrize("error", [ConnectionError("reset"), ReadTimeout("slow")])
def test_retries_network_error_once_then_succeeds(error):
    send = Mock(side_effect=[error, "ok"])
    sleep = Mock()

    assert send_with_network_retry(send, label="test", sleep=sleep) == "ok"

    assert send.call_count == 2
    sleep.assert_called_once_with(0.5)


def test_propagates_last_network_error_after_retries(caplog):
    send = Mock(side_effect=ConnectionError("reset"))
    sleep = Mock()

    with pytest.raises(ConnectionError):
        send_with_network_retry(
            send, label="KIS /uapi/test", sleep=sleep, delays=(0.1, 0.2)
        )

    assert send.call_count == 3
    assert sleep.call_args_list == [call(0.1), call(0.2)]
    assert "target=KIS /uapi/test" in caplog.text


def test_does_not_retry_non_network_errors():
    send = Mock(side_effect=HTTPError("500"))
    sleep = Mock()

    with pytest.raises(HTTPError):
        send_with_network_retry(send, label="test", sleep=sleep)

    send.assert_called_once_with()
    sleep.assert_not_called()
