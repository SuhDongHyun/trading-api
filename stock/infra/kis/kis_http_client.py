import logging
from json import JSONDecodeError
from typing import Any, Callable

import requests
from requests import Response

from config import KISSetting
from stock.infra.kis.kis_rate_limiter import KisRateLimiter
from stock.infra.kis.kis_token_manager import KisTokenManager

logger = logging.getLogger(__name__)
SENSITIVE_HEADER_KEYS = {"authorization", "appkey", "appsecret"}
KIS_REQUEST_TIMEOUT_SECONDS = 10
KIS_EXPIRED_TOKEN_MSG_CODE = "EGW00123"


def safe_headers(headers: dict[str, str]) -> dict[str, str]:
    """인증 정보가 로그에 남지 않도록 민감 헤더를 제거한다."""

    return {
        key: value
        for key, value in headers.items()
        if key.lower() not in SENSITIVE_HEADER_KEYS
    }


def is_expired_token_response(resp: Response) -> bool:
    """KIS가 토큰 만료를 HTTP 오류 본문으로 보낸 경우에만 갱신을 허용한다."""

    if resp.status_code < 400:
        return False

    try:
        body = resp.json()
    except (JSONDecodeError, ValueError):
        return False

    return body.get("msg_cd") == KIS_EXPIRED_TOKEN_MSG_CODE


class KisHttpClient:
    """프로세스에서 Singleton으로 공유하며 KIS 인증·호출 제한·만료 재시도를 적용한다."""

    def __init__(
        self,
        kis_settings: KISSetting,
        token_manager: KisTokenManager,
        rate_limiter: KisRateLimiter,
        get: Callable[..., Response] | None = None,
        post: Callable[..., Response] | None = None,
    ):
        self._settings = kis_settings
        self._token_manager = token_manager
        self._rate_limiter = rate_limiter
        self._get = get or requests.get
        self._post = post or requests.post

    def get(
        self,
        path: str,
        params: dict[str, str] | None = None,
        tr_id: str | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Response:
        params = params or {}
        return self._api_request(
            "GET",
            self._get,
            path,
            tr_id=tr_id,
            extra_headers=extra_headers,
            payload_name="params",
            payload=params,
            params=params,
        )

    def post(
        self,
        path: str,
        body: dict[str, Any] | None = None,
        tr_id: str | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Response:
        body = body or {}
        return self._api_request(
            "POST",
            self._post,
            path,
            tr_id=tr_id,
            extra_headers=extra_headers,
            payload_name="body",
            payload=body,
            json=body,
        )

    def _send_request(
        self,
        method: str,
        request_func: Callable[..., Response],
        url: str,
        headers: dict[str, str],
        tr_id: str | None,
        payload_name: str,
        payload: dict[str, Any],
        **request_kwargs: Any,
    ) -> Response:
        self._rate_limiter.acquire()
        try:
            return request_func(
                url=url,
                headers=headers,
                timeout=KIS_REQUEST_TIMEOUT_SECONDS,
                **request_kwargs,
            )
        except (requests.ConnectionError, requests.Timeout):
            logger.exception(
                "KIS %s connection failed url=%s tr_id=%s %s=%s headers=%s",
                method,
                url,
                tr_id,
                payload_name,
                payload,
                safe_headers(headers),
            )
            raise

    def _api_request(
        self,
        method: str,
        request_func: Callable[..., Response],
        path: str,
        *,
        tr_id: str | None,
        extra_headers: dict[str, str] | None,
        payload_name: str,
        payload: dict[str, Any],
        **request_kwargs: Any,
    ) -> Response:
        """공통 인증과 응답 처리를 적용해 KIS API를 호출한다."""

        url = f"{self._settings.base_url}{path}"
        auth_headers = {"tr_id": tr_id} if tr_id else None
        headers = self._token_manager.auth_headers(auth_headers)
        if extra_headers:
            headers.update(extra_headers)

        resp = self._send_request(
            method,
            request_func,
            url,
            headers,
            tr_id,
            payload_name,
            payload,
            **request_kwargs,
        )

        # KIS는 만료 토큰을 특정 msg_cd로만 식별할 수 있어 해당 응답만 1회 재시도한다.
        if is_expired_token_response(resp):
            logger.info("KIS token expired; refreshing access token and retrying once")
            headers = self._token_manager.auth_headers(auth_headers, force_refresh=True)
            if extra_headers:
                headers.update(extra_headers)
            resp = self._send_request(
                method,
                request_func,
                url,
                headers,
                tr_id,
                payload_name,
                payload,
                **request_kwargs,
            )

        if resp.status_code >= 400:
            logger.error(
                "KIS %s failed status=%s url=%s tr_id=%s %s=%s headers=%s body=%s",
                method,
                resp.status_code,
                resp.url,
                tr_id,
                payload_name,
                payload,
                safe_headers(headers),
                resp.text,
            )

        resp.raise_for_status()
        return resp
