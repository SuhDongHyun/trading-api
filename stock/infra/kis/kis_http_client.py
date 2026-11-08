import logging
from time import sleep as time_sleep
from typing import Callable
from urllib.parse import urlsplit

import requests
from requests import Response

from common.network_retry import send_with_network_retry
from config import KISSetting
from stock.domain.exceptions import ExternalApiError, ExternalApiUnavailableError
from stock.infra.kis.kis_rate_limiter import KisRateLimiter
from stock.infra.kis.kis_token_manager import KisTokenManager

KIS_REQUEST_TIMEOUT_SECONDS = 10
KIS_EXPIRED_TOKEN_MSG_CODE = "EGW00123"
KIS_RATE_LIMIT_MSG_CODE = "EGW00201"
KIS_TRANSIENT_MSG_CODES = frozenset(
    {
        "EGW00316",
        "OPSQ1002",
        "EGW00001",
        "EGW00301",
        "OPSQ0010",
        "OPSQ0011",
        KIS_RATE_LIMIT_MSG_CODE,
    }
)
KIS_RETRY_DELAYS_SECONDS = (0.3, 0.6)
# KIS 유량 제한은 초 단위 창으로 집계되므로 창이 넘어갈 만큼 기다린다.
KIS_RATE_LIMIT_RETRY_DELAYS_SECONDS = (1.0, 1.0)

logger = logging.getLogger(__name__)


def _json_body(resp: Response) -> dict | None:
    try:
        body = resp.json()
    except ValueError:
        return None
    return body if isinstance(body, dict) else None


def is_expired_token_response(resp: Response) -> bool:
    """KIS가 토큰 만료를 HTTP 오류 본문으로 보낸 경우에만 갱신을 허용한다."""

    if resp.status_code < 400:
        return False

    body = _json_body(resp)
    if body is None:
        return False
    return body.get("msg_cd") == KIS_EXPIRED_TOKEN_MSG_CODE


def is_transient_error_response(resp: Response) -> bool:
    """HTTP 오류 또는 KIS 업무 오류 본문의 일시적 오류 코드를 판별한다."""

    body = _json_body(resp)
    return bool(
        body
        and body.get("msg_cd") in KIS_TRANSIENT_MSG_CODES
        and (
            resp.status_code >= 400
            or (
                200 <= resp.status_code < 300
                and body.get("rt_cd") is not None
                and body.get("rt_cd") != "0"
            )
        )
    )


class KisHttpClient:
    """Singleton HTTP 클라이언트로 KIS 인증, 호출 제한, 만료 토큰 재시도를 적용한다."""

    def __init__(
        self,
        kis_settings: KISSetting,
        token_manager: KisTokenManager,
        rate_limiter: KisRateLimiter,
        get: Callable[..., Response] | None = None,
        sleep: Callable[[float], None] | None = None,
    ):
        self._settings = kis_settings
        self._token_manager = token_manager
        self._rate_limiter = rate_limiter
        self._get = get or requests.get
        self._sleep = sleep or time_sleep

    def get(
        self,
        path: str,
        params: dict[str, str] | None = None,
        tr_id: str | None = None,
    ) -> Response:
        """인증 토큰과 호출 간격을 적용해 KIS GET 요청을 보낸다."""

        params = params or {}
        url = f"{self._settings.base_url}{path}"
        auth_headers = {"tr_id": tr_id} if tr_id else None
        headers = self._token_manager.auth_headers(auth_headers)
        resp = self._send_request(url, headers, params)
        request_count = 1

        # KIS는 만료 토큰을 특정 msg_cd로만 식별할 수 있어 해당 응답만 1회 재시도한다.
        if is_expired_token_response(resp):
            headers = self._token_manager.auth_headers(auth_headers, force_refresh=True)
            resp = self._send_request(url, headers, params)
            request_count += 1

        retry_index = 0
        while is_transient_error_response(resp):
            body = _json_body(resp) or {}
            delays = (
                KIS_RATE_LIMIT_RETRY_DELAYS_SECONDS
                if body.get("msg_cd") == KIS_RATE_LIMIT_MSG_CODE
                else KIS_RETRY_DELAYS_SECONDS
            )
            if retry_index >= len(delays):
                raise ExternalApiUnavailableError(
                    "외부 API가 일시적으로 응답하지 않습니다. 잠시 후 다시 시도해 주세요.",
                    diagnostic=(
                        f"KIS GET unavailable path={path} tr_id={tr_id} "
                        f"msg_cd={body.get('msg_cd')} msg1={body.get('msg1')} "
                        f"status={resp.status_code} attempts={request_count}"
                    ),
                )

            logger.warning(
                "KIS transient error, retrying path=%s tr_id=%s msg_cd=%s "
                "status=%s attempt=%s delay=%s",
                path,
                tr_id,
                body.get("msg_cd"),
                resp.status_code,
                request_count,
                delays[retry_index],
            )
            self._sleep(delays[retry_index])
            resp = self._send_request(url, headers, params)
            request_count += 1
            retry_index += 1

        resp.raise_for_status()
        body = _json_body(resp)
        if body is None:
            return resp

        if "rt_cd" in body and body["rt_cd"] != "0":
            raise ExternalApiError(
                "KIS API 요청에 실패했습니다.",
                diagnostic=(
                    f"KIS GET failed path={path} tr_id={tr_id} "
                    f"msg_cd={body.get('msg_cd')} msg1={body.get('msg1')}"
                ),
            )
        return resp

    def _send_request(
        self,
        url: str,
        headers: dict[str, str],
        params: dict[str, str],
    ) -> Response:
        """공유 호출 제한을 통과한 뒤 KIS GET을 보내고, 네트워크 오류는 1회 재시도한다."""

        def send() -> Response:
            self._rate_limiter.acquire()
            return self._get(
                url=url,
                headers=headers,
                timeout=KIS_REQUEST_TIMEOUT_SECONDS,
                params=params,
            )

        return send_with_network_retry(
            send, label=f"KIS {urlsplit(url).path}", sleep=self._sleep
        )
