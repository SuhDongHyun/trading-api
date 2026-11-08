"""멱등 GET 요청의 일시적 네트워크 오류를 짧게 대기한 뒤 다시 시도한다."""

import logging
from time import sleep as time_sleep
from typing import Callable, TypeVar

import requests

logger = logging.getLogger(__name__)

NETWORK_RETRY_DELAYS_SECONDS = (0.5,)
RETRYABLE_NETWORK_ERRORS = (requests.ConnectionError, requests.Timeout)

T = TypeVar("T")


def send_with_network_retry(
    send: Callable[[], T],
    *,
    label: str,
    sleep: Callable[[float], None] = time_sleep,
    delays: tuple[float, ...] = NETWORK_RETRY_DELAYS_SECONDS,
) -> T:
    """연결 실패·타임아웃만 재시도하고, 마지막 시도의 예외는 그대로 전파한다.

    `send`는 호출 제한 획득까지 포함해야 재시도 요청도 같은 제한을 통과한다.
    """

    for attempt, delay in enumerate(delays, start=1):
        try:
            return send()
        except RETRYABLE_NETWORK_ERRORS as exc:
            logger.warning(
                "Network error, retrying target=%s type=%s attempt=%s delay=%s",
                label,
                type(exc).__name__,
                attempt,
                delay,
            )
            sleep(delay)
    return send()
